"""Closed learning loop: cwd project detection, task sessions, episodes,
promotion to memories, decay/contradiction flags, quality metrics."""
from __future__ import annotations
import json, pathlib, re, subprocess

from cortex.langs import redact
from cortex.db import code_root
from cortex import search

VALID_OUTCOMES = ("implemented", "tested", "verified", "failed", "partial", "abandoned")
CODE_EXTS = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".py", ".go", ".sql", ".prisma")
MIN_SAMPLE = 3
INVARIANT_MARKERS = ("never", "always", "must", "invariant", "ensure", "لا يمكن", "يجب")


# ---------- project detection from filesystem ----------

def detect_cwd(con, cwd: str | None = None) -> tuple[str | None, list[str]]:
    """Return (project_id|None, ambiguous_candidates). Longest indexed path prefix wins."""
    rp = pathlib.Path(cwd or pathlib.Path.cwd()).resolve()
    best, best_len = None, -1
    for p in con.execute("SELECT id,path FROM projects"):
        pp = pathlib.Path(p["path"]).resolve()
        if rp == pp or pp in rp.parents:
            n = len(pp.parts)
            if n > best_len:
                best, best_len = p["id"], n
    if best:
        return best, []
    # git worktrees live outside the indexed prefix; map via git-common-dir
    g = subprocess.run(["git", "-C", str(rp), "rev-parse", "--git-common-dir"],
                       capture_output=True, text=True)
    if g.returncode == 0 and g.stdout.strip():
        common = pathlib.Path(g.stdout.strip())
        if not common.is_absolute():
            common = (rp / common).resolve()
        for p in con.execute("SELECT id,path FROM projects"):
            pp = pathlib.Path(p["path"]).resolve()
            if common == pp or pp in common.parents or pp in common.parents:
                return p["id"], []
    name = rp.name.lower()
    hits = [r["id"] for r in con.execute(
        "SELECT id FROM projects WHERE id=? OR LOWER(name)=?", (name, name))]
    return (hits[0] if len(hits) == 1 else None), hits


def resolve_project(con, explicit: str | None = None, cwd: str | None = None):
    """explicit > cwd detection > basename. Raises ValueError on ambiguity."""
    if explicit:
        row = con.execute("SELECT id FROM projects WHERE id=?", (explicit,)).fetchone()
        if not row:
            raise ValueError(f"unknown project '{explicit}' (see `cortex projects`)")
        return explicit
    pid, cands = detect_cwd(con, cwd)
    if pid:
        return pid
    if len(cands) > 1:
        raise ValueError(f"ambiguous project name; candidates: {', '.join(sorted(cands))}")
    return None


def _git(path: str, *args: str) -> str:
    r = subprocess.run(["git", "-C", path, *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def live_git(project_path: str, indexed_commit: str | None = None) -> dict:
    """Read current git state, including a live commit distance when possible."""
    head = _git(project_path, "rev-parse", "HEAD").strip()[:12]
    dirty = sum(1 for l in _git(project_path, "status", "--porcelain").splitlines() if l.strip())
    indexed = (indexed_commit or "")[:12]
    behind: int | None = 0 if head and indexed and head == indexed else None
    if head and indexed and head != indexed:
        count = _git(project_path, "rev-list", "--count", f"{indexed}..{head}").strip()
        if count.isdigit():
            behind = int(count)
    return {"head": head, "dirty": dirty, "indexed": indexed, "behind": behind}


def freshness_status(gitinfo: dict) -> str:
    """Compact machine-readable freshness state shared by CLI and MCP."""
    if not gitinfo.get("head"):
        return "no_git"
    changed_head = gitinfo.get("head") != gitinfo.get("indexed")
    if gitinfo.get("dirty"):
        return "behind/dirty" if changed_head else "dirty"
    return "behind" if changed_head else "fresh"


# ---------- packet parsing for suggestions ----------

def _raw_lines(packet: str, name: str) -> list[str]:
    m = re.search(rf"\n## {re.escape(name)}\n(.*?)(?=\n## |\Z)", packet, re.S)
    return [l.strip() for l in m.group(1).splitlines() if l.strip()] if m else []


def parse_suggestions(packet: str) -> dict:
    files: list[str] = []
    for sec in ("PRIMARY FILES", "START HERE", "READ FIRST"):
        for line in _raw_lines(packet, sec):
            tok = line.lstrip("- ").split()[0] if line.split() else ""
            if tok.endswith(CODE_EXTS):
                files.append(tok)
    tests: list[str] = []
    for line in _raw_lines(packet, "TESTS"):
        m = re.search(r"\]\s+(\S+)$", line)
        if m:
            tests.append(m.group(1))
        elif line.startswith(("test", "src/test")):
            tests.append(line.split()[0])
    symbols = []
    for line in _raw_lines(packet, "PRIMARY SYMBOLS"):
        parts = line.split(" ", 2)
        if len(parts) >= 3:
            symbols.append({"path": parts[0], "name": parts[1]})
    return {"files": list(dict.fromkeys(files))[:25], "symbols": symbols[:40], "tests": tests[:20]}


# ---------- session lifecycle ----------

def task_start(con, task: str, project: str | None = None, budget: int = 3000,
               cwd: str | None = None) -> dict:
    from cortex.contextpack import context as ctx_fn  # lazy: contextpack lazily imports session
    pid = None
    try:
        pid = resolve_project(con, project, cwd)
    except ValueError as e:
        return {"error": str(e)}
    if not pid:
        pid = search.detect_named_project(con, task)
    p = con.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone() if pid else None
    if not p:
        return {"error": f"no project resolved for task {task!r}; pass --project"}
    gitinfo = live_git(code_root(p), p["indexed_commit"])
    fresh = freshness_status(gitinfo)
    ctx = ctx_fn(con, task, project_id=pid, budget=budget)
    if "error" in ctx:
        return ctx
    sug = parse_suggestions(ctx["packet"])
    cur = con.execute(
        """INSERT INTO task_sessions(project_id, task, start_head, brain_freshness, context_chars,
           files_suggested_json, symbols_suggested_json, tests_suggested_json, dirty_at_start_json)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (pid, redact(task)[:500], gitinfo["head"], fresh, len(ctx["packet"]),
         json.dumps(sug["files"]), json.dumps([s["name"] for s in sug["symbols"]]),
         json.dumps(sug["tests"]), json.dumps(_dirty_list(p))))
    con.commit()
    sid = cur.lastrowid
    log_event(con, sid, "context", f"budget={budget} tokens~{ctx.get('tokens_est')}")
    return {"session_id": sid, "project": pid, "freshness": fresh,
            "tokens_est": ctx.get("tokens_est"), "packet": ctx["packet"],
            **{f"suggested_{k}": v for k, v in sug.items()},
            "_hint": "`cortex impact` before risky edits; `cortex task complete` when done"}


def _dirty_list(p) -> list[str]:
    out = []
    for line in _git(code_root(p), "status", "--porcelain").splitlines():
        if line.strip():
            out.append(line[3:].strip().split(" -> ")[-1])
    return out[:200]


def get_session(con, session_id: int):
    s = con.execute("SELECT * FROM task_sessions WHERE id=?", (session_id,)).fetchone()
    if not s:
        raise ValueError(f"no session #{session_id}")
    return s


def log_event(con, session_id: int, kind: str, detail: str):
    con.execute("INSERT INTO session_events(session_id, kind, detail) VALUES (?,?,?)",
                (session_id, kind, redact(str(detail))[:400]))
    con.commit()


def record_impact(con, session_id: int, target: str, result: dict) -> dict:
    s = get_session(con, session_id)
    queries = json.loads(s["impact_queries_json"] or "[]")
    queries.append({"target": target[:200], "risk": result.get("risk"),
                    "targets": result.get("targets", [])[:5]})
    con.execute("UPDATE task_sessions SET impact_queries_json=? WHERE id=?",
                (json.dumps(queries)[:8000], session_id))
    con.commit()
    log_event(con, session_id, "impact", target)
    return {"recorded": True, "queries": len(queries)}


# ---------- completion: evidence gathering + episode generation ----------

def changed_files(prow, start_head: str, dirty_at_start: list[str] | None = None
                  ) -> tuple[list[str], bool]:
    """Files changed BY THIS SESSION: committed range + new worktree dirt,
    excluding files that were already dirty before the task started."""
    end_head = _git(code_root(prow), "rev-parse", "HEAD").strip()
    paths: set[str] = set()
    all_committed = True
    committed_range: set[str] = set()
    if start_head and end_head:
        out = _git(code_root(prow), "diff", "--name-only", f"{start_head}..{end_head}")
        committed_range = {l.strip() for l in out.splitlines() if l.strip()}
        paths |= committed_range
    pre_existing = set(dirty_at_start or [])
    wt = [l[3:].strip().split(" -> ")[-1]
          for l in _git(code_root(prow), "status", "--porcelain").splitlines()]
    for w in wt:
        if not w:
            continue
        all_committed = False
        # attribute only NEW dirt; pre-existing dirty files count only if also committed
        if w not in pre_existing or w in committed_range:
            paths.add(w)
    return sorted(paths), all_committed


def symbols_touched(con, prow, files: list[str], since_head: str | None) -> dict[str, list[str]]:
    res: dict[str, list[str]] = {}
    rng = f"{since_head}..HEAD" if since_head else "HEAD"
    for f in files[:30]:
        if not f.endswith(CODE_EXTS):
            continue
        syms = [r["name"] for r in con.execute(
            "SELECT name FROM symbols WHERE project_id=? AND path=?", (prow["id"], f))]
        if not syms:
            continue
        patch = _git(code_root(prow), "diff", rng, "--", f)[:20000]
        hit = [s for s in syms if s in patch]
        if hit:
            res[f] = hit[:15]
    return res


def compute_metrics(sug_files: list[str], touched: list[str],
                    sug_tests: list[str], tests_run: list[str] | None) -> dict:
    sug_set, touch_set = set(sug_files), set(touched)
    inter = sug_set & touch_set
    m: dict = {
        "files_suggested": len(sug_set),
        "files_touched": len(touch_set),
        "primary_precision": round(len(inter) / len(sug_set), 2) if sug_set else None,
        "suggestion_recall": round(len(inter) / len(touch_set), 2) if touch_set else None,
    }
    if tests_run is not None:
        m["tests_run"] = len(tests_run)
        m["test_hit_rate"] = round(
            len(set(tests_run) & set(sug_tests)) / len(tests_run), 2) if sug_tests else None
    return m


def task_complete(con, session_id: int, outcome: str = "implemented",
                  problem: str | None = None, root_cause: str | None = None,
                  lessons: str | None = None, failed_approaches: str | None = None,
                  solution: str | None = None, tests_run: list[str] | None = None,
                  commit_sha: str | None = None, auto_promote: bool = True) -> dict:
    if outcome not in VALID_OUTCOMES:
        raise ValueError(f"outcome must be one of {VALID_OUTCOMES}")
    s = get_session(con, session_id)
    if s["completed_at"]:
        raise ValueError(f"session #{session_id} already completed ({s['outcome']})")
    pid = s["project_id"]
    prow = con.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()

    touched: list[str] = []
    all_committed = True
    if prow:
        touched, all_committed = changed_files(
            prow, s["start_head"], json.loads(s["dirty_at_start_json"] or "[]"))
    code_touched = [t for t in touched if t.endswith(CODE_EXTS)]

    metrics = compute_metrics(json.loads(s["files_suggested_json"] or "[]"), code_touched,
                              json.loads(s["tests_suggested_json"] or "[]"), tests_run)

    # deterministic evidence
    syms_by_file = symbols_touched(con, prow, code_touched, s["start_head"]) if prow else {}
    sym_names = sorted({n for v in syms_by_file.values() for n in v})
    modules = sorted({m["slug"] for f in code_touched
                      if (m := search.module_for_path(con, pid, f))})
    apis = sorted({f"{a['method']} {a['route']}" for f in code_touched
                   for a in search.apis_for_path(con, pid, f, limit=10)})
    dbents = sorted({d["name"] for f in code_touched
                     for d in search.db_entities_for_file(con, pid, f)})
    mapped_tests = sorted({t["path"] for t in
                           search.tests_for_paths(con, pid, code_touched, limit=20)})

    if outcome in ("tested", "verified") and not touched:
        raise ValueError("no file changes recorded for this session; "
                         "use --outcome implemented/partial, or make and commit the change first")

    end_git = live_git(code_root(prow), prow["indexed_commit"]) if prow else {"head": "", "dirty": 0}
    final_sha = commit_sha or (end_git["head"] if (all_committed and end_git["head"]) else None)
    commits_in_range = len(_git(code_root(prow), "log", "--oneline",
                                f"{s['start_head']}..{end_git['head']}").splitlines()) \
        if (prow and s["start_head"] and end_git["head"]) else 0
    metrics["commits_in_range"] = commits_in_range

    lessons = redact(lessons).strip() if lessons else None
    if not any([lessons, problem, root_cause]) and outcome == "abandoned":
        # nothing durable to learn from an empty abandoned task
        con.execute("""UPDATE task_sessions SET outcome=?, end_head=?, completed_at=datetime('now'),
                       files_touched_json=?, episode_id=NULL, metrics_json=? WHERE id=?""",
                    (outcome, end_git["head"], json.dumps(code_touched)[:4000],
                     json.dumps(metrics), session_id))
        con.commit()
        return {"episode": None, "metrics": metrics,
                "note": "abandoned with no durable knowledge; session closed without episode"}

    if not solution:
        bits = [f"{len(code_touched)} file(s): {', '.join(code_touched[:5])}"]
        if sym_names:
            bits.append(f"symbols: {', '.join(sym_names[:8])}")
        if tests_run:
            bits.append(f"tests run: {len(tests_run)}")
        elif mapped_tests:
            bits.append("mapped tests exist but run-status unconfirmed")
        solution = "; ".join(bits)

    conf = "verified" if (final_sha and lessons) else (
        "strongly_inferred" if (final_sha or tests_run) else "inferred")

    cur = con.execute(
        """INSERT INTO episodes(project_id, task, problem, root_cause, files_modified_json,
           solution, failed_approaches, lessons, commit_sha, parent_sha, status, outcome,
           confidence, module_slugs_json, symbols_json, apis_json, db_entities_json,
           tests_run_json, evidence_files_json, session_id, metrics_json)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (pid, s["task"], redact(problem) if problem else None,
         redact(root_cause) if root_cause else None,
         json.dumps(code_touched[:300]), redact(solution)[:3000],
         redact(failed_approaches) if failed_approaches else None,
         lessons, (final_sha or "")[:12] or None,
         s["start_head"] or None,
         "active", outcome, conf,
         json.dumps(modules[:60]), json.dumps(sym_names[:120]),
         json.dumps(apis[:40]), json.dumps(dbents[:80]),
         json.dumps(redacted_tests(tests_run))[:2000],
         json.dumps(code_touched[:300]), session_id, json.dumps(metrics)))
    eid = cur.lastrowid
    ep_row = con.execute("SELECT problem, root_cause, solution, lessons FROM episodes WHERE id=?",
                         (eid,)).fetchone()
    con.execute("INSERT INTO fts_episodes(rowid, task, problem, root_cause, solution, lessons) "
                "VALUES (?,?,?,?,?,?)",
                (eid, s["task"], ep_row["problem"] or "", ep_row["root_cause"] or "",
                 ep_row["solution"] or "", ep_row["lessons"] or ""))
    con.execute("""UPDATE task_sessions SET outcome=?, end_head=?, completed_at=datetime('now'),
                   episode_id=?, metrics_json=? WHERE id=?""",
                (outcome, end_git["head"], eid, json.dumps(metrics), session_id))
    con.commit()

    promoted = None
    try:
        if auto_promote and lessons and outcome in ("implemented", "tested", "verified") \
                and any(mk in lessons.lower() for mk in INVARIANT_MARKERS):
            promoted = promote_episode(con, eid)
    except Exception:
        promoted = None
    log_event(con, session_id, "complete", f"outcome={outcome} episode={eid}")
    return {"episode_id": eid, "confidence": conf, "status": "active",
            "evidence": {"files": code_touched, "symbols": sym_names[:15], "modules": modules,
                         "apis": apis[:10], "db_entities": dbents[:10],
                         "mapped_tests": mapped_tests[:10]},
            "metrics": metrics, "promoted_memory_id": promoted}


def redacted_tests(tests: list[str] | None) -> list[str]:
    return [redact(t)[:200] for t in (tests or [])]


# ---------- promotion ----------

def promote_episode(con, episode_id: int, scope: str | None = None) -> int | None:
    ep = con.execute("SELECT * FROM episodes WHERE id=?", (episode_id,)).fetchone()
    if not ep or not ep["lessons"]:
        return None
    all_kw = set(search.keywords(ep["lessons"]))
    proj_ids = {r["id"].lower() for r in con.execute("SELECT id FROM projects")}
    lesson_kw = {k for k in all_kw if k not in proj_ids}   # project names carry no meaning
    if scope is None:
        scope = "module" if ep["module_slugs_json"] and ep["module_slugs_json"] != "[]" else "pitfall"
    # episodes are single-project facts: global requires an explicit human decision
    # dedup only against memories of the SAME project+scope — a lesson from one
    # repo must never suppress a distinct lesson from another
    for mem in con.execute("SELECT id,title,body_md FROM memories WHERE COALESCE(project_id,'')=? "
                           "AND scope=?", (ep["project_id"] or "", scope)):
        have = set(search.keywords(mem["title"] + " " + mem["body_md"]))
        if lesson_kw and len(lesson_kw & have) / max(len(lesson_kw), 1) >= 0.7:
            return None
    title = redact(f"{ep['task'][:80]}")
    cur = con.execute(
        """INSERT INTO memories(scope, project_id, title, body_md, confidence, origin,
           source_files_json, verified_at_commit, stale, derived_from, status)
           VALUES (?,?,?,?,?,?,?,?,0,?,'active')""",
        (scope, ep["project_id"], title,
         redact(ep["lessons"])[:3000] + f"\n\n[derived_from: episode:{ep['id']} @ {ep['commit_sha']}]",
         ep["confidence"] if ep["confidence"] != "inferred" else "inferred",
         "generated", ep["files_modified_json"], ep["commit_sha"],
         f"episode:{ep['id']}"))
    con.commit()
    _sync_memory_fts(con, cur.lastrowid)
    return cur.lastrowid


def _sync_memory_fts(con, memory_id: int):
    m = con.execute("SELECT * FROM memories WHERE id=?", (memory_id,)).fetchone()
    if not m:
        return
    con.execute("INSERT OR REPLACE INTO fts_memories(rowid, title, body) VALUES (?,?,?)",
                (memory_id, m["title"] or "", m["body_md"] or ""))
    con.commit()


def supersede_episode(con, old_id: int, new_id: int | None = None, status: str = "superseded"):
    if status not in ("superseded", "obsolete", "uncertain", "active"):
        raise ValueError(f"bad status {status}")
    con.execute("UPDATE episodes SET status=?, superseded_by=? WHERE id=?",
                (status, new_id, old_id))
    # propagate to generated memories
    con.execute("UPDATE memories SET status=? WHERE derived_from=? AND origin='generated'",
                (status, f"episode:{old_id}"))
    con.commit()


# ---------- decay / contradiction ----------

def decay_check(con, project_id: str | None = None) -> dict:
    """Flag episodes whose evidence vanished; propagate to generated memories.
    Contradiction candidates reported, never silently deleted."""
    where, args = ("WHERE project_id=?" , [project_id]) if project_id else ("", [])
    obsolete = uncertain = contradictions = 0
    for ep in con.execute(f"SELECT * FROM episodes {where}", args):
        try:
            ev_files = json.loads(ep["files_modified_json"] or "[]")
            ev_syms = json.loads(ep["symbols_json"] or "[]")
        except json.JSONDecodeError:
            continue  # corrupt row; flagged by doctor repair, never crash the loop
        if ep["status"] in ("obsolete", "uncertain"):
            # reversible: evidence fully restored -> back to active
            restored = all(
                con.execute("SELECT 1 FROM files WHERE project_id=? AND path=?",
                            (ep["project_id"], f)).fetchone() for f in ev_files)
            if ev_files and restored:
                con.execute("UPDATE episodes SET status='active' WHERE id=?", (ep["id"],))
                con.execute("""UPDATE memories SET status='active'
                               WHERE derived_from=? AND origin='generated'""",
                            (f"episode:{ep['id']}",))
            continue
        if ep["status"] not in ("active", "uncertain"):
            continue
        evidence = ev_files
        missing = [f for f in evidence
                   if not (con.execute("SELECT 1 FROM files WHERE project_id=? AND path=?",
                                       (ep["project_id"], f)).fetchone())]
        gone_syms = [s for s in ev_syms
                     if not con.execute("SELECT 1 FROM symbols WHERE project_id=? AND name=?",
                                        (ep["project_id"], s)).fetchone()]
        new_status = None
        if evidence and len(missing) == len(evidence):
            new_status = "obsolete"
        elif ev_syms and gone_syms and len(gone_syms) == len(ev_syms):
            new_status = "uncertain"
        if new_status and new_status != ep["status"]:
            con.execute("UPDATE episodes SET status=? WHERE id=?", (new_status, ep["id"]))
            con.execute("UPDATE memories SET status=? WHERE derived_from=? AND origin='generated'",
                        (new_status, f"episode:{ep['id']}"))
            if new_status == "obsolete":
                obsolete += 1
            else:
                uncertain += 1
    # contradiction candidates: newer active episode overlapping files of an obsolete/uncertain one
    seen_pairs = set()
    for old in con.execute("SELECT id,project_id,files_modified_json FROM episodes "
                           "WHERE status IN ('obsolete','uncertain')"):
        try:
            olds = set(json.loads(old["files_modified_json"] or "[]"))
        except json.JSONDecodeError:
            continue
        for new in con.execute("SELECT id,files_modified_json FROM episodes "
                               "WHERE project_id=? AND status='active' AND id>? ORDER BY id DESC LIMIT 5",
                               (old["project_id"], old["id"])):
            try:
                news = set(json.loads(new["files_modified_json"] or "[]"))
            except json.JSONDecodeError:
                continue
            if len(olds & news) >= 2 and (old["id"], new["id"]) not in seen_pairs:
                seen_pairs.add((old["id"], new["id"]))
                contradictions += 1
                break
    con.commit()
    return {"obsolete_marked": obsolete, "uncertain_marked": uncertain,
            "contradiction_candidates": contradictions}


# ---------- retrieval ----------

def relevant_episodes(con, pid: str | None, task: str, limit: int = 3) -> list:
    kws = set(search.keywords(task))
    if not kws:
        return []
    rows = con.execute(
        "SELECT * FROM episodes WHERE (? IS NULL OR project_id=?) AND status='active' "
        "AND outcome != 'abandoned' ORDER BY id DESC LIMIT 60", (pid, pid)).fetchall()
    scored = []
    for ep in rows:
        hay = " ".join(filter(None, [ep["task"], ep["problem"], ep["root_cause"],
                                     ep["lessons"], (ep["symbols_json"] or ""),
                                     (ep["apis_json"] or ""), (ep["db_entities_json"] or ""),
                                     (ep["module_slugs_json"] or "")])).lower()
        overlap = sum(1 for k in kws if k in hay)
        if overlap >= max(1, min(2, len(kws) // 3)):
            scored.append((overlap, ep))
    scored.sort(key=lambda x: (-x[0], -x[1]["id"]))
    return [ep for _, ep in scored[:limit]]


# ---------- quality report ----------

def quality_report(con) -> dict:
    def one(sql, *a):
        return con.execute(sql, a).fetchone()[0]
    sessions_done = one("SELECT COUNT(*) FROM task_sessions WHERE completed_at IS NOT NULL")
    precs, recs, thits = [], [], []
    for (outcome, mj) in con.execute("""SELECT outcome, metrics_json FROM task_sessions
                                        WHERE metrics_json IS NOT NULL"""):
        m = json.loads(mj)
        # only real implementation tasks that changed code carry precision ground truth
        if not m.get("files_touched") or outcome in ("failed", "abandoned"):
            continue
        if m.get("primary_precision") is not None:
            precs.append(m["primary_precision"])
        if m.get("suggestion_recall") is not None:
            recs.append(m["suggestion_recall"])
        if m.get("test_hit_rate") is not None:
            thits.append(m["test_hit_rate"])
    def avg(xs):
        # below MIN_SAMPLE a rate is noise, not signal — report None
        return round(sum(xs) / len(xs), 2) if len(xs) >= MIN_SAMPLE else None
    return {
        "measured_tasks": len(precs),
        "sessions_started": one("SELECT COUNT(*) FROM task_sessions"),
        "sessions_completed": sessions_done,
        "episodes_total": one("SELECT COUNT(*) FROM episodes"),
        "episodes_active": one("SELECT COUNT(*) FROM episodes WHERE status='active'"),
        "episodes_failed_lessons": one("SELECT COUNT(*) FROM episodes WHERE outcome='failed'"),
        "episodes_uncertain": one("SELECT COUNT(*) FROM episodes WHERE status='uncertain'"),
        "episodes_obsolete": one("SELECT COUNT(*) FROM episodes WHERE status='obsolete'"),
        "memories_generated": one("SELECT COUNT(*) FROM memories WHERE origin='generated'"),
        "stale_memories": one("SELECT COUNT(*) FROM memories WHERE stale=1"),
        "primary_file_hit_rate": avg(precs),
        "suggestion_recall": avg(recs),
        "test_hit_rate": avg(thits),
    }
