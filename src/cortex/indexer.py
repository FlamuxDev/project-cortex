"""Indexing engine: full + incremental."""
from __future__ import annotations
from contextlib import contextmanager
import hashlib, json, os, pathlib, posixpath, re, subprocess, sys, tempfile, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from cortex import extractors, gitmine
from cortex.db import code_root, connect, state_get, state_set
from cortex.discovery import discover_projects, scan_file_tree
from cortex.langs import is_code, is_test, lang_of, redact

INDEX_FORMAT_VERSION = "2"


def sha1(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()[:12]


def _hash_file_into(digest, path: pathlib.Path) -> None:
    try:
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
    except OSError:
        digest.update(b"<missing>")


def worktree_fingerprint(root: pathlib.Path | str) -> str:
    """Fingerprint the exact indexable working-tree state.

    Git repositories are cheap: clean trees reduce to HEAD, while only dirty
    code paths are content-hashed. Non-git projects hash their indexable files.
    Documentation-only edits therefore do not trigger a code re-index.
    """
    root = pathlib.Path(root)
    digest = hashlib.sha256()
    try:
        head_run = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, timeout=30, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        head_run = None
    if head_run is not None and head_run.returncode == 0:
        digest.update(b"git\0")
        digest.update(head_run.stdout.strip())
        try:
            status_run = subprocess.run(
                ["git", "-C", str(root), "status", "--porcelain=v1", "-z",
                 "--untracked-files=all"],
                capture_output=True, timeout=30, check=False,
            )
            raw = status_run.stdout if status_run.returncode == 0 else None
        except (OSError, subprocess.SubprocessError):
            raw = None
        if raw is None:
            # Fail closed: a broken git status must not collapse to a clean HEAD.
            # Hash the discoverable tree instead, preserving correctness at the
            # cost of a slower check.
            digest.update(b"\0status-unavailable\0")
            for rel in scan_file_tree(root):
                digest.update(rel.encode("utf-8", "surrogateescape") + b"\0")
                _hash_file_into(digest, root / rel)
            return digest.hexdigest()
        parts = raw.split(b"\0")
        i = 0
        while i < len(parts):
            record = parts[i]
            i += 1
            if len(record) < 4:
                continue
            status = record[:2]
            candidates = [record[3:]]
            if any(code in status for code in (b"R", b"C")) and i < len(parts):
                candidates.append(parts[i])
                i += 1
            for raw_path in candidates:
                rel = raw_path.decode("utf-8", "surrogateescape")
                if not is_code(rel):
                    continue
                digest.update(b"\0" + status + b"\0" + raw_path + b"\0")
                _hash_file_into(digest, root / rel)
        return digest.hexdigest()

    digest.update(b"tree\0")
    for rel in scan_file_tree(root):
        digest.update(rel.encode("utf-8", "surrogateescape") + b"\0")
        _hash_file_into(digest, root / rel)
    return digest.hexdigest()


def _clean_git_fingerprint(head: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(b"git\0")
    digest.update(head.strip())
    return digest.hexdigest()


def _record_worktree_sync(con, pid: str, root: pathlib.Path,
                          started_fingerprint: str, stats: dict) -> None:
    finished = worktree_fingerprint(root)
    stable = finished == started_fingerprint
    marker = f"{INDEX_FORMAT_VERSION}:{finished}" if stable else ""
    state_set(con, f"worktree:{pid}", marker)
    stats["index_sync"] = "current" if stable else "changed-during-index"


def _lock_dir(con) -> pathlib.Path:
    row = con.execute("PRAGMA database_list").fetchone()
    db_file = pathlib.Path(row["file"]) if row and row["file"] else None
    if db_file:
        return db_file.parent / "locks"
    return pathlib.Path(tempfile.gettempdir()) / f"project-cortex-{os.getpid()}-locks"


def _dead_lock_owner(lock_path: pathlib.Path) -> bool:
    try:
        body = lock_path.read_text(errors="replace")[:100]
        match = re.search(r"\bpid=(\d+)\b", body)
        if not match:
            return False
        os.kill(int(match.group(1)), 0)
    except ProcessLookupError:
        return True
    except (OSError, ValueError):
        return False
    return False


@contextmanager
def project_refresh_lock(con, project_id: str, timeout: float = 30.0):
    """Serialize per-project refreshes across independent MCP processes."""
    lock_root = _lock_dir(con)
    lock_root.mkdir(parents=True, exist_ok=True)
    safe_id = re.sub(r"[^a-zA-Z0-9_.-]+", "-", project_id)
    lock_path = lock_root / f"{safe_id}.lock"
    deadline = time.monotonic() + max(timeout, 0)
    acquired = False
    while not acquired:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            try:
                stale = (_dead_lock_owner(lock_path) or
                         time.time() - lock_path.stat().st_mtime > 1800)
            except OSError:
                stale = False
            if stale:
                try:
                    lock_path.unlink()
                except OSError:
                    pass
                continue
            if time.monotonic() >= deadline:
                raise TimeoutError(f"timed out waiting for refresh lock for {project_id}")
            time.sleep(0.05)
        else:
            try:
                os.write(fd, f"pid={os.getpid()} time={time.time()}\n".encode())
            finally:
                os.close(fd)
            acquired = True
    try:
        yield
    finally:
        if acquired:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "x"


# ------------------------------------------------------------------ import resolution
def _import_suffix_index(file_set: set[str]) -> dict[str, str]:
    """Map every path suffix to its shortest deterministic repository path."""
    index: dict[str, str] = {}
    for path in sorted(file_set, key=lambda item: (len(item), item)):
        parts = path.split("/")
        for start in range(len(parts)):
            index.setdefault("/".join(parts[start:]), path)
    return index


def resolve_import(spec: str, from_path: str, file_set: set[str], project_id: str,
                   suffix_index: dict[str, str] | None = None) -> str | None:
    """Resolve an import specifier to a repo-relative file path when possible."""
    if spec.startswith(("node:", "http")) :
        return None
    base = None
    if spec.startswith("./") or spec.startswith("../"):
        base = posixpath.dirname(from_path)
        spec = posixpath.normpath(posixpath.join(base, spec))
    elif spec.startswith(("@/", "~/")):
        spec = "src/" + spec[2:]

    exts = ["", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".py", ".go"]
    indexes = ["index.ts", "index.tsx", "index.js", "__init__.py", "index.go"]
    cands = [spec + e for e in exts] + [posixpath.join(spec, ix) for ix in indexes]
    for c in cands:
        if c in file_set:
            return c
    # Python import extraction includes the imported name
    # (``from cortex.db import connect`` -> ``cortex.db.connect``). Walk back
    # through dotted components and accept src-layout suffixes.
    if "." in spec and " " not in spec and not spec.endswith(".ts"):
        suffixes = suffix_index if suffix_index is not None else _import_suffix_index(file_set)
        dotted = spec.split(".")
        for width in range(len(dotted), 0, -1):
            pc = "/".join(dotted[:width])
            for c in [pc + ".py", posixpath.join(pc, "__init__.py")]:
                if c in suffixes:
                    return suffixes[c]
    # alias fallback: match by progressively longer path SUFFIXES (handles @/, monorepo roots)
    norm = spec.lstrip("./").lstrip("@/")
    suffixes = suffix_index if suffix_index is not None else _import_suffix_index(file_set)
    parts = norm.split("/")
    for width in range(len(parts), 0, -1):
        tail = "/".join(parts[-width:])
        for c in [tail + e for e in exts] + [posixpath.join(tail, ix) for ix in indexes]:
            if c in suffixes:
                return suffixes[c]
    return None


# ------------------------------------------------------------------ indexing core
def index_project(con, proj: dict, full: bool = True) -> dict:
    t0 = time.time()
    root = pathlib.Path(proj.get("repo_path") or proj["path"])
    pid = proj["id"]
    head = proj.get("git_head")
    started_fingerprint = worktree_fingerprint(root)

    prev_row = con.execute("SELECT indexed_commit FROM projects WHERE id=?", (pid,)).fetchone()
    prev_head = prev_row["indexed_commit"] if prev_row else None
    had_index = bool(prev_row and con.execute(
        "SELECT 1 FROM files WHERE project_id=? LIMIT 1", (pid,)).fetchone())

    con.execute("""INSERT INTO projects(id,name,path,repo_path,kind,languages,frameworks,git_head,status)
                   VALUES (?,?,?,?,?,?,?,?, 'active')
                   ON CONFLICT(id) DO UPDATE SET name=excluded.name, path=excluded.path,
                     repo_path=excluded.repo_path, kind=excluded.kind,
                     languages=excluded.languages, frameworks=excluded.frameworks,
                     git_head=excluded.git_head""",
                (pid, proj["name"], proj["path"], proj.get("repo_path") or proj["path"],
                 proj["kind"], proj["top_exts"], proj.get("frameworks") or None, head))
    con.commit()

    files = scan_file_tree(root)
    file_set = set(files)
    suffix_index = _import_suffix_index(file_set)

    if not full and had_index:
        stats = _incremental(con, pid, root, files, file_set, prev_head, head)
        _record_worktree_sync(con, pid, root, started_fingerprint, stats)
        return stats

    # ---- full index: wipe deterministic rows, keep curated memories/modules
    # FTS tables are contentless. Delete their rows while the source rowids still
    # exist; doing this after deleting symbols/files leaves unjoinable ghosts.
    _delete_project_fts(con, pid)
    for t in ["files", "symbols", "refs", "apis", "db_entities", "tests", "commits",
              "commit_files"]:
        con.execute(f"DELETE FROM {t} WHERE project_id=?", (pid,))

    stats = {"files": 0, "symbols": 0, "refs": 0, "routes": 0, "tables": 0, "tests": 0}
    for rel in files:
        p = root / rel
        try:
            raw = p.read_bytes()
        except OSError:
            continue
        lang = lang_of(rel)
        is_t = is_test(rel)
        loc = raw.count(b"\n") + 1
        h = sha1(raw)
        res = extractors.extract(raw, lang, rel) if lang else extractors.new_result(rel)

        con.execute("""INSERT OR REPLACE INTO files(project_id,path,lang,ext,loc,hash,is_test,is_entry)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (pid, rel, lang, pathlib.Path(rel).suffix, loc, h, int(is_t),
                     int(_is_entry(rel))))
        stats["files"] += 1

        for s in res["symbols"]:
            con.execute("""INSERT INTO symbols(project_id,path,name,kind,parent,line_start,line_end,
                           signature,doc,exported) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                        (pid, rel, s["name"], s["kind"], s["parent"], s["line_start"], s["line_end"],
                         redact(s["signature"] or "")[:200], redact(s["doc"] or "")[:400],
                         s["exported"]))
            stats["symbols"] += 1
        for r in res["refs"]:
            dst_path = None
            if r["kind"] == "import":
                dst_path = resolve_import(r["dst_name"], rel, file_set, pid, suffix_index)
            con.execute("INSERT INTO refs(project_id,src_path,dst_name,dst_path,kind,line) VALUES (?,?,?,?,?,?)",
                        (pid, rel, r["dst_name"][:300], dst_path, r["kind"], r.get("line")))
            stats["refs"] += 1
        clientish = any(k in rel.lower() for k in ("components/", "screens/", "hooks/", "pages/", "app/")) and lang in ("ts", "tsx", "js", "jsx")
        direction = "client" if clientish and not rel.endswith(("route.ts", "route.tsx")) else "server"
        for rt in res["routes"]:
            con.execute("INSERT INTO apis(project_id,method,route,handler_path,handler_symbol,auth,direction) VALUES (?,?,?,?,?,?,?)",
                        (pid, rt["method"], rt["route"], rel, rt.get("handler_symbol"), rt.get("auth"), direction))
            stats["routes"] += 1
        for tb in res["tables"]:
            con.execute("INSERT INTO db_entities(project_id,name,kind,file_path) VALUES (?,?,?,?)",
                        (pid, tb["name"], tb["kind"], rel))
            stats["tables"] += 1
        if is_t:
            kind = ("e2e" if "/e2e/" in rel or "e2e" in rel.split("/")[:3] else
                    "integration" if "integration" in rel.lower() else "unit")
            con.execute("INSERT INTO tests(project_id,path,name,kind) VALUES (?,?,?,?)",
                        (pid, rel, pathlib.Path(rel).stem, kind))
            stats["tests"] += 1

    # test -> target mapping via imports
    _refresh_test_targets(con, pid)

    # Next.js app-router routes (file conventions)
    _index_nextjs_routes(con, pid, file_set)

    con.commit()
    _recompute_importance(con, pid)
    _mine_git(con, pid, str(root))
    con.execute("""DELETE FROM module_files WHERE project_id=? AND path NOT IN
                   (SELECT path FROM files WHERE project_id=?)""", (pid, pid))
    _refresh_fts(con, pid)

    con.execute("""UPDATE projects SET indexed_commit=?, last_indexed_at=datetime('now') WHERE id=?""",
                (head, pid))
    state_set(con, f"indexed:{pid}", head or "")
    con.commit()
    stats["secs"] = round(time.time() - t0, 1)
    _record_worktree_sync(con, pid, root, started_fingerprint, stats)
    return stats


def _is_entry(rel: str) -> bool:
    b = posixpath.basename(rel)
    return b in {"main.ts", "main.js", "index.ts", "index.js", "app.ts", "server.ts", "server.js",
                 "main.py", "__main__.py", "manage.py", "run_agent.py", "wsgi.py", "asgi.py",
                 "page.tsx", "layout.tsx", "route.ts"} or b.startswith("main.go")


def _index_nextjs_routes(con, pid, file_set):
    for f in file_set:
        parts = f.split("/")
        if "app" in parts and (f.endswith("route.ts") or f.endswith("route.tsx")):
            i = parts.index("app")
            route = "/" + "/".join(p for p in parts[i + 1:-1] if not (p.startswith("(") and p.endswith(")")))
            for m in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                con.execute("""INSERT INTO apis(project_id,method,route,handler_path,handler_symbol)
                               SELECT ?,?,?,?,'exported '||? WHERE EXISTS(SELECT 1 FROM symbols
                                 WHERE project_id=? AND path=? AND name=? AND exported=1)""",
                            (pid, m, route, f, m, pid, f, m))


def _recompute_importance(con, pid):
    con.execute("""
        UPDATE files SET importance =
          (SELECT COUNT(*) FROM refs r WHERE r.project_id=files.project_id AND r.dst_path=files.path) * 1.0
          + CASE WHEN is_entry=1 THEN 5 ELSE 0 END
          + COALESCE((SELECT COUNT(*) FROM apis a WHERE a.project_id=files.project_id AND a.handler_path=files.path)*3, 0)
          + MAX(0, 10 - (SELECT COUNT(*) FROM commits c JOIN commit_files cf
                ON cf.project_id=c.project_id AND cf.sha=c.sha
                WHERE c.project_id=files.project_id AND cf.path=files.path AND c.category='fix') )
    """)
    con.execute("""UPDATE files SET importance =
          importance + (SELECT COUNT(*)*0.5 FROM refs r
                        WHERE r.project_id=files.project_id
                          AND r.src_path=files.path AND r.kind='import')
          WHERE project_id=?""", (pid,))
    # The previous correlated ``LIKE '%symbol'`` query scanned every call edge
    # once per symbol (minutes on large Python repositories). Extractors emit
    # plain or qualified call names, so aggregate their final identifier once.
    call_counts: dict[str, int] = {}
    for row in con.execute("""SELECT dst_name,COUNT(*) n FROM refs
                              WHERE project_id=? AND kind='call'
                              GROUP BY dst_name""", (pid,)):
        parts = re.findall(r"[A-Za-z_][A-Za-z0-9_$]*", row["dst_name"] or "")
        if parts:
            call_counts[parts[-1]] = call_counts.get(parts[-1], 0) + row["n"]
    updates = []
    for row in con.execute("""SELECT id,name,kind,exported FROM symbols
                              WHERE project_id=?""", (pid,)):
        importance = (float(call_counts.get(row["name"], 0)) +
                      (2 if row["exported"] else 0) +
                      (1 if row["kind"] in {"class", "function", "component", "method"} else 0))
        updates.append((importance, row["id"]))
    con.executemany("UPDATE symbols SET importance=? WHERE id=?", updates)
    con.commit()


def _mine_git(con, pid, root):
    commits = gitmine.mine_history(root)
    known = {r[0] for r in con.execute("SELECT sha FROM commits WHERE project_id=?", (pid,))}
    new = [c for c in commits if c["sha"] not in known]
    for c in new:
        con.execute("INSERT OR IGNORE INTO commits(project_id,sha,date,author,subject,category) VALUES (?,?,?,?,?,?)",
                    (pid, c["sha"], c["date"], c["author"], redact(c["subject"]), c["category"]))
        for f in c["files"][:200]:
            con.execute("INSERT OR IGNORE INTO commit_files(project_id,sha,path) VALUES (?,?,?)",
                        (pid, c["sha"], f))
    con.commit()


FTS_BATCH = 500
# Symbols indexed for full-text search per project. The old hard-coded 20k left
# large repos partly unsearchable by name with no signal that it had happened.
FTS_SYMBOL_CAP = int(os.environ.get("CORTEX_FTS_SYMBOL_CAP", "100000"))
FTS_FILE_CAP = int(os.environ.get("CORTEX_FTS_FILE_CAP", "20000"))


def _delete_project_fts(con, pid: str) -> None:
    """Remove one project's contentless FTS rows before source rows disappear."""
    con.execute("DELETE FROM fts_symbols WHERE rowid IN "
                "(SELECT id FROM symbols WHERE project_id=?)", (pid,))
    con.execute("DELETE FROM fts_files WHERE rowid IN "
                "(SELECT rowid FROM files WHERE project_id=?)", (pid,))


def _prune_orphan_fts(con) -> None:
    """Repair ghosts left by interrupted or pre-0.3 indexing runs."""
    con.execute("DELETE FROM fts_symbols WHERE rowid NOT IN (SELECT id FROM symbols)")
    con.execute("DELETE FROM fts_files WHERE rowid NOT IN (SELECT rowid FROM files)")


def _refresh_fts(con, pid):
    _prune_orphan_fts(con)
    con.execute("DELETE FROM fts_symbols WHERE rowid IN (SELECT id FROM symbols WHERE project_id=?)", (pid,))
    rows = con.execute("""SELECT s.rowid AS rid, s.name, s.signature, s.doc, s.path FROM symbols s
                          WHERE s.project_id=? ORDER BY s.importance DESC LIMIT ?""", (pid, FTS_SYMBOL_CAP)).fetchall()
    batch = []
    for r in rows:
        batch.append((r["rid"], r["name"], r["signature"] or "", r["doc"] or "", r["path"]))
        if len(batch) >= FTS_BATCH:
            con.executemany("INSERT INTO fts_symbols(rowid,name,sig,doc,path) VALUES (?,?,?,?,?)", batch)
            batch = []
    if batch:
        con.executemany("INSERT INTO fts_symbols(rowid,name,sig,doc,path) VALUES (?,?,?,?,?)", batch)
    con.execute("DELETE FROM fts_files WHERE rowid IN (SELECT rowid FROM files WHERE project_id=?)", (pid,))
    from cortex.langs import content_terms
    prow = con.execute("SELECT path, repo_path FROM projects WHERE id=?", (pid,)).fetchone()
    root = pathlib.Path(code_root(prow)) if prow else None
    rows = con.execute("SELECT rowid AS rid, path FROM files WHERE project_id=? ORDER BY importance DESC LIMIT ?",
                       (pid, FTS_FILE_CAP)).fetchall()
    batch = []
    for r in rows:
        terms = ""
        if root is not None:
            try:
                raw = (root / r["path"]).read_bytes()[:200000]
                terms = content_terms(raw.decode("utf-8", "replace"))
            except OSError:
                terms = ""
        batch.append((r["rid"], r["path"], terms))
        if len(batch) >= FTS_BATCH:
            con.executemany("INSERT INTO fts_files(rowid,path,terms) VALUES (?,?,?)", batch)
            batch = []
    if batch:
        con.executemany("INSERT INTO fts_files(rowid,path,terms) VALUES (?,?,?)", batch)
    _refresh_memory_fts(con)


def _refresh_memory_fts(con):
    con.execute("DELETE FROM fts_memories")  # memories rebuilt wholesale
    rows = con.execute("SELECT rowid AS rid, title, body_md FROM memories").fetchall()
    con.executemany("INSERT INTO fts_memories(rowid,title,body) VALUES (?,?,?)",
                    [(r["rid"], r["title"], r["body_md"]) for r in rows])
    con.commit()


def _incremental(con, pid, root: pathlib.Path, files: list[str], file_set: set[str],
                 prev_head: str | None, head: str | None) -> dict:
    """Re-extract only changed files; refresh derived tables."""
    t0 = time.time()
    changed, added, removed = [], [], []
    old_files = {r["path"]: r["hash"] for r in
                 con.execute("SELECT path,hash FROM files WHERE project_id=?", (pid,))}
    suffix_index = _import_suffix_index(file_set)
    dirty = 0
    for rel in files:
        try:
            raw = (root / rel).read_bytes()
        except OSError:
            continue
        h = sha1(raw)
        if rel not in old_files:
            added.append(rel)
        elif old_files[rel] != h:
            changed.append(rel)
    removed = [p for p in old_files if p not in file_set]

    # uncommitted working-tree changes vs HEAD
    import subprocess
    st = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                        capture_output=True, text=True)
    dirty = len([l for l in st.stdout.splitlines() if l.strip()])
    # changed files per git status are already covered by hash comparison above.

    reindexed = set(changed) | set(added) | set(removed)
    if reindexed:
        marks = ",".join("?" for _ in reindexed)
        args = (pid, *sorted(reindexed))
        con.execute(f"DELETE FROM fts_symbols WHERE rowid IN (SELECT id FROM symbols "
                    f"WHERE project_id=? AND path IN ({marks}))", args)
        con.execute(f"DELETE FROM fts_files WHERE rowid IN (SELECT rowid FROM files "
                    f"WHERE project_id=? AND path IN ({marks}))", args)
    for rel in reindexed:
        con.execute("DELETE FROM symbols WHERE project_id=? AND path=?", (pid, rel))
        con.execute("DELETE FROM refs WHERE project_id=? AND src_path=?", (pid, rel))
        con.execute("DELETE FROM apis WHERE project_id=? AND handler_path=?", (pid, rel))
        con.execute("DELETE FROM db_entities WHERE project_id=? AND file_path=?", (pid, rel))
        con.execute("DELETE FROM tests WHERE project_id=? AND path=?", (pid, rel))
        con.execute("DELETE FROM files WHERE project_id=? AND path=?", (pid, rel))
    # mark memories touching changed paths stale
    for rel in reindexed:
        con.execute("""UPDATE memories SET stale=1 WHERE project_id=? AND (
                       source_files_json LIKE ? OR evidence_json LIKE ?)""",
                    (pid, f'%"{rel}"%', f'%{rel}%'))

    # re-extract changed/added
    for rel in sorted(set(changed) | set(added)):
        p = root / rel
        try:
            raw = p.read_bytes()
        except OSError:
            continue
        lang = lang_of(rel)
        res = extractors.extract(raw, lang, rel) if lang else {"symbols": [], "refs": [], "routes": [], "tables": []}
        loc = raw.count(b"\n") + 1
        test_file = is_test(rel)
        con.execute("""INSERT OR REPLACE INTO files(project_id,path,lang,ext,loc,hash,is_test,is_entry)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (pid, rel, lang, pathlib.Path(rel).suffix, loc, sha1(raw),
                     int(test_file), int(_is_entry(rel))))
        for s in res["symbols"]:
            con.execute("""INSERT INTO symbols(project_id,path,name,kind,parent,line_start,line_end,signature,doc,exported)
                           VALUES (?,?,?,?,?,?,?,?,?,?)""",
                        (pid, rel, s["name"], s["kind"], s["parent"], s["line_start"], s["line_end"],
                         redact(s["signature"] or "")[:200], redact(s["doc"] or "")[:400], s["exported"]))
        for r in res["refs"]:
            dst_path = resolve_import(r["dst_name"], rel, file_set, pid, suffix_index) if r["kind"] == "import" else None
            con.execute("INSERT INTO refs(project_id,src_path,dst_name,dst_path,kind,line) VALUES (?,?,?,?,?,?)",
                        (pid, rel, r["dst_name"][:300], dst_path, r["kind"], r.get("line")))
        clientish = any(k in rel.lower() for k in ("components/", "screens/", "hooks/", "pages/", "app/")) and lang in ("ts", "tsx", "js", "jsx")
        direction = "client" if clientish and not rel.endswith(("route.ts", "route.tsx")) else "server"
        for rt in res["routes"]:
            con.execute("INSERT INTO apis(project_id,method,route,handler_path,handler_symbol,auth,direction) VALUES (?,?,?,?,?,?,?)",
                        (pid, rt["method"], rt["route"], rel, rt.get("handler_symbol"), rt.get("auth"), direction))
        for tb in res["tables"]:
            con.execute("INSERT INTO db_entities(project_id,name,kind,file_path) VALUES (?,?,?,?)",
                        (pid, tb["name"], tb["kind"], rel))
        if test_file:
            kind = ("e2e" if "/e2e/" in rel or "e2e" in rel.split("/")[:3] else
                    "integration" if "integration" in rel.lower() else "unit")
            con.execute("INSERT INTO tests(project_id,path,name,kind) VALUES (?,?,?,?)",
                        (pid, rel, pathlib.Path(rel).stem, kind))

    if head != prev_head:
        _mine_git(con, pid, str(root))
    if added or removed:
        _refresh_import_paths(con, pid, file_set)
    _refresh_test_targets(con, pid)
    _recompute_importance(con, pid)
    _refresh_fts(con, pid)
    con.execute("""UPDATE projects SET indexed_commit=?, last_indexed_at=datetime('now'),
                   dirty_files=? WHERE id=?""", (head, dirty, pid))
    con.commit()
    return {"changed": len(changed), "added": len(added), "removed": len(removed),
            "dirty": dirty, "stale_memories": con.execute(
                "SELECT COUNT(*) c FROM memories WHERE project_id=? AND stale=1", (pid,)).fetchone()["c"],
            "secs": round(time.time() - t0, 1)}


def _refresh_test_targets(con, pid: str) -> None:
    """Rebuild test-to-target mappings after either full or incremental extraction."""
    con.execute("UPDATE tests SET targets_json=NULL WHERE project_id=?", (pid,))
    agg: dict[str, list[str]] = {}
    for tr in con.execute("""SELECT DISTINCT r.src_path, r.dst_path FROM refs r
                             JOIN files f ON f.project_id=r.project_id AND f.path=r.src_path
                             WHERE r.project_id=? AND r.kind='import' AND f.is_test=1
                               AND r.dst_path IS NOT NULL""", (pid,)):
        agg.setdefault(tr["src_path"], []).append(tr["dst_path"])
    for test_path, targets in agg.items():
        con.execute("UPDATE tests SET targets_json=? WHERE project_id=? AND path=?",
                    (json.dumps(sorted(set(targets))), pid, test_path))


def _refresh_import_paths(con, pid: str, file_set: set[str],
                          unresolved_only: bool = False) -> None:
    """Re-resolve unchanged imports after files are added or removed."""
    suffix_index = _import_suffix_index(file_set)
    sql = ("SELECT rowid,src_path,dst_name,dst_path FROM refs "
           "WHERE project_id=? AND kind='import'")
    if unresolved_only:
        sql += " AND dst_path IS NULL"
    updates = []
    for row in con.execute(sql, (pid,)):
        resolved = resolve_import(row["dst_name"], row["src_path"], file_set,
                                  pid, suffix_index)
        if resolved != row["dst_path"]:
            updates.append((resolved, row["rowid"]))
    con.executemany("UPDATE refs SET dst_path=? WHERE rowid=?", updates)


def _repair_index_format(con, pid: str) -> dict:
    """Repair derived rows after an index-format upgrade without re-parsing code."""
    file_set = {row["path"] for row in con.execute(
        "SELECT path FROM files WHERE project_id=?", (pid,))}
    existing_tests = {row["path"] for row in con.execute(
        "SELECT path FROM tests WHERE project_id=?", (pid,))}
    added_tests = 0
    for row in con.execute("""SELECT path FROM files WHERE project_id=? AND is_test=1
                              ORDER BY path""", (pid,)):
        path = row["path"]
        if path in existing_tests:
            continue
        kind = ("e2e" if "/e2e/" in path or "e2e" in path.split("/")[:3] else
                "integration" if "integration" in path.lower() else "unit")
        con.execute("INSERT INTO tests(project_id,path,name,kind) VALUES (?,?,?,?)",
                    (pid, path, pathlib.Path(path).stem, kind))
        added_tests += 1
    _refresh_import_paths(con, pid, file_set, unresolved_only=True)
    _refresh_test_targets(con, pid)
    con.commit()
    return {"from": "legacy", "to": INDEX_FORMAT_VERSION,
            "refs_resolved": con.execute("""SELECT COUNT(*) n FROM refs
                WHERE project_id=? AND kind='import' AND dst_path IS NOT NULL""",
                (pid,)).fetchone()["n"], "test_rows_added": added_tests}


def _stored_index_matches_clean_git(stored, root: pathlib.Path,
                                    fingerprint: str) -> bool:
    try:
        run = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                             capture_output=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return False
    head = run.stdout.strip() if run.returncode == 0 else b""
    indexed = (stored["indexed_commit"] or "").encode()
    return (bool(head) and head[:12] == indexed[:12] and
            fingerprint == _clean_git_fingerprint(head))


def update_project(con, project_id: str, full: bool = False) -> dict:
    stored = con.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    if not stored:
        raise ValueError(f"unknown project {project_id}")
    root = pathlib.Path(code_root(stored))
    if not root.is_dir():
        raise ValueError(f"project path does not exist: {root}")
    try:
        head_run = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=30, check=False,
        )
        head = head_run.stdout.strip() if head_run.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        head = None
    proj = {
        "id": stored["id"], "name": stored["name"], "path": stored["path"],
        "repo_path": code_root(stored), "kind": stored["kind"],
        "top_exts": stored["languages"] or "", "frameworks": stored["frameworks"],
        "git_head": head,
    }
    return index_project(con, proj, full=full)


def refresh_project(con, project_id: str, mode: str = "auto",
                    lock_timeout: float = 30.0) -> dict:
    """Refresh an index only when its code snapshot changed.

    Modes: ``auto`` fingerprints and updates when needed, ``never`` is a
    read-only diagnostic path, and ``force`` always runs an incremental update.
    """
    if mode not in {"auto", "never", "force"}:
        raise ValueError("refresh must be auto, never, or force")
    stored = con.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    if not stored:
        raise ValueError(f"unknown project {project_id}")
    root = pathlib.Path(code_root(stored))
    if mode == "never":
        return {"mode": mode, "status": "skipped", "synced": False}
    if not root.is_dir():
        return {"mode": mode, "status": "failed", "synced": False,
                "error": f"project path does not exist: {root}"}

    current = worktree_fingerprint(root)
    recorded = state_get(con, f"worktree:{project_id}", "")
    expected = f"{INDEX_FORMAT_VERSION}:{current}"
    if mode == "auto" and recorded == expected:
        return {"mode": mode, "status": "current", "synced": True}

    try:
        with project_refresh_lock(con, project_id, timeout=lock_timeout):
            current = worktree_fingerprint(root)
            recorded = state_get(con, f"worktree:{project_id}", "")
            expected = f"{INDEX_FORMAT_VERSION}:{current}"
            if mode == "auto" and recorded == expected:
                return {"mode": mode, "status": "current", "synced": True,
                        "reason": "refreshed by another process"}
            needs_format_repair = not recorded.startswith(f"{INDEX_FORMAT_VERSION}:")
            repair = _repair_index_format(con, project_id) if needs_format_repair else None
            if repair and _stored_index_matches_clean_git(stored, root, current):
                stats = {"changed": 0, "added": 0, "removed": 0,
                         "format_repair": repair}
                _record_worktree_sync(con, project_id, root, current, stats)
            else:
                stats = update_project(con, project_id, full=False)
                if repair:
                    stats["format_repair"] = repair
    except Exception as exc:
        return {"mode": mode, "status": "failed", "synced": False,
                "error": str(exc)[:300]}

    synced = (state_get(con, f"worktree:{project_id}", "") ==
              f"{INDEX_FORMAT_VERSION}:{worktree_fingerprint(root)}")
    return {"mode": mode,
            "status": "refreshed" if synced else "unstable",
            "synced": synced, "stats": stats}


def index_all(con, only: list[str] | None = None) -> dict[str, dict]:
    results = {}
    for proj in discover_projects():
        if only and proj["id"] not in only:
            continue
        try:
            results[proj["id"]] = index_project(con, proj, full=True)
        except Exception as e:
            results[proj["id"]] = {"error": str(e)}
            con.execute("UPDATE projects SET status='error' WHERE id=?", (proj["id"],))
            con.commit()
    return results


if __name__ == "__main__":
    con = connect()
    which = sys.argv[1:] or None
    for pid, stats in index_all(con, which).items():
        print(pid, stats)
