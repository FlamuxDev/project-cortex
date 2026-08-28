"""Indexing engine: full + incremental."""
from __future__ import annotations
import hashlib, json, os, pathlib, posixpath, re, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from cortex import extractors, gitmine
from cortex.db import code_root, connect, state_set
from cortex.langs import is_test, lang_of, redact
from cortex.discovery import discover_projects, scan_file_tree


def sha1(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()[:12]


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "x"


# ------------------------------------------------------------------ import resolution
def resolve_import(spec: str, from_path: str, file_set: set[str], project_id: str) -> str | None:
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
    # python dotted
    if "." in spec and " " not in spec and not spec.endswith(".ts"):
        pc = spec.replace(".", "/")
        for c in [pc + ".py", posixpath.join(pc, "__init__.py")]:
            if c in file_set:
                return c
    # alias fallback: match by progressively longer path SUFFIXES (handles @/, monorepo roots)
    norm = spec.lstrip("./").lstrip("@/")
    parts = norm.split("/")
    for width in range(len(parts), 0, -1):
        tail = "/".join(parts[-width:])
        for c in [tail + e for e in exts] + [posixpath.join(tail, ix) for ix in indexes]:
            if c in file_set:
                return c
    return None


# ------------------------------------------------------------------ indexing core
def index_project(con, proj: dict, full: bool = True) -> dict:
    t0 = time.time()
    root = pathlib.Path(proj.get("repo_path") or proj["path"])
    pid = proj["id"]
    head = proj.get("git_head")

    prev_head = con.execute("SELECT indexed_commit FROM projects WHERE id=?", (pid,)).fetchone()
    prev_head = prev_head["indexed_commit"] if prev_head else None

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

    if not full and prev_head:
        return _incremental(con, pid, root, files, file_set, prev_head, head)

    # ---- full index: wipe deterministic rows, keep curated memories/modules
    # FTS tables are contentless. Delete their rows while the source rowids still
    # exist; doing this after deleting symbols/files leaves unjoinable ghosts.
    _delete_project_fts(con, pid)
    for t in ["files", "symbols", "refs", "apis", "db_entities", "tests", "commits",
              "commit_files", "module_files"]:
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
                dst_path = resolve_import(r["dst_name"], rel, file_set, pid)
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
    _refresh_fts(con, pid)

    con.execute("""UPDATE projects SET indexed_commit=?, last_indexed_at=datetime('now') WHERE id=?""",
                (head, pid))
    state_set(con, f"indexed:{pid}", head or "")
    con.commit()
    stats["secs"] = round(time.time() - t0, 1)
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
    con.execute("""UPDATE symbols SET importance =
          COALESCE((SELECT COUNT(*) FROM refs r WHERE r.project_id=symbols.project_id
                    AND r.kind='call' AND (r.dst_name LIKE '%'||symbols.name)), 0) * 1.0
          + CASE WHEN exported=1 THEN 2 ELSE 0 END
          + CASE WHEN kind IN ('class','function','component','method') THEN 1 ELSE 0 END
          WHERE project_id=?""", (pid,))
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
            dst_path = resolve_import(r["dst_name"], rel, file_set, pid) if r["kind"] == "import" else None
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


def _refresh_import_paths(con, pid: str, file_set: set[str]) -> None:
    """Re-resolve unchanged imports after files are added or removed."""
    rows = con.execute("SELECT rowid,src_path,dst_name FROM refs "
                       "WHERE project_id=? AND kind='import'", (pid,)).fetchall()
    updates = [(resolve_import(r["dst_name"], r["src_path"], file_set, pid), r["rowid"])
               for r in rows]
    con.executemany("UPDATE refs SET dst_path=? WHERE rowid=?", updates)


def update_project(con, project_id: str) -> dict:
    projs = discover_projects()
    proj = next((p for p in projs if p["id"] == project_id), None)
    if not proj:
        raise ValueError(f"unknown project {project_id}")
    return index_project(con, proj, full=False)


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
