"""Cortex CLI."""
from __future__ import annotations
import argparse, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from cortex.db import connect
from cortex import indexer, search
from cortex.contextpack import context_text, impact as impact_fn


def cmd_projects(args):
    con = connect()
    for p in con.execute("SELECT * FROM projects ORDER BY id"):
        print(f"{p['id']:18} {p['kind'] or '?':10} fresh={'yes' if p['git_head']==p['indexed_commit'] else 'STALE':6} files={con.execute('SELECT COUNT(*) FROM files WHERE project_id=?', (p['id'],)).fetchone()[0]:5}  {p['path']}")


def _freshness(con, pid):
    p = con.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    if not p:
        return None
    # LIVE git state — never trust stored values for freshness
    import subprocess
    head = subprocess.run(["git", "-C", p["path"], "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip() or None
    dirty = len([l for l in subprocess.run(["git", "-C", p["path"], "status", "--porcelain"],
                 capture_output=True, text=True).stdout.splitlines() if l.strip()])
    behind = 0
    if head and p["indexed_commit"] and head[:12] != p["indexed_commit"][:12]:
        row = con.execute("""SELECT COUNT(*) c FROM commits WHERE project_id=? AND date >=
                             COALESCE((SELECT date FROM commits WHERE project_id=? AND sha LIKE ?),'1970-01-01')""",
                          (pid, pid, p["indexed_commit"][:12] + "%")).fetchone()
        behind = max(row["c"] - 1, 0)
    return {"head": (head or "")[:12], "indexed": (p["indexed_commit"] or "")[:12],
            "behind": behind, "dirty": dirty,
            "status": ("FRESH" if behind == 0 else f"BEHIND {behind} commits")
                      + (f" (+{dirty} uncommitted)" if dirty else "")}


def cmd_status(args):
    con = connect()
    pid = args.project or (search.detect_project(con, args.task) if args.task else None)
    if not pid:
        total_files = con.execute("SELECT COUNT(*) c FROM files").fetchone()["c"]
        total_syms = con.execute("SELECT COUNT(*) c FROM symbols").fetchone()["c"]
        nproj = con.execute("SELECT COUNT(*) c FROM projects").fetchone()["c"]
        print(f"cortex v0.1 | projects: {nproj} | files indexed: {total_files} | symbols: {total_syms}")
        print("run `cortex projects` for the list")
        return
    p = con.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    f = _freshness(con, pid)
    def count(sql):
        return con.execute(sql, (pid,)).fetchone()[0]
    print(f"Project:   {p['name']} ({pid})")
    print(f"Path:      {p['path']}")
    print(f"HEAD:      {f['head']}   Brain commit: {f['indexed']}")
    print(f"Freshness: {f['status']}" + (f" (+{f['dirty']} dirty)" if f['dirty'] else ""))
    print(f"Files:     {count('SELECT COUNT(*) FROM files WHERE project_id=?')}")
    print(f"Symbols:   {count('SELECT COUNT(*) FROM symbols WHERE project_id=?')}")
    print(f"Modules:   {count('SELECT COUNT(*) FROM modules WHERE project_id=?')}")
    print(f"Flows:     {count('SELECT COUNT(*) FROM flows WHERE project_id=?')}")
    print(f"APIs:      {count('SELECT COUNT(*) FROM apis WHERE project_id=?')}")
    print(f"DB ents:   {count('SELECT COUNT(*) FROM db_entities WHERE project_id=?')}")
    print(f"Tests:     {count('SELECT COUNT(*) FROM tests WHERE project_id=?')}")
    print(f"Decisions: {count('SELECT COUNT(*) FROM decisions WHERE project_id=?')}")
    print(f"Memories:  {count('SELECT COUNT(*) FROM memories WHERE project_id=?')}"
          f" ({count('SELECT COUNT(*) FROM memories WHERE project_id=? AND stale=1')} stale)")


def cmd_context(args):
    con = connect()
    if getattr(args, "all", False):
        from cortex.contextpack import context_cross
        print(context_cross(con, args.task, budget=args.budget)["packet"])
        return
    pid = _proj(con, args)
    print(context_text(con, args.task, project_id=pid,
                       budget=_budget(args.budget)))


def cmd_search(args):
    con = connect()
    pid = _proj(con, args) or search.detect_project(con, args.query)
    for kind, fn in [("symbol", search.search_symbols), ("memory", search.search_memories),
                     ("file", search.search_files)]:
        rows = fn(con, pid, args.query, limit=args.limit)
        if rows:
            print(f"--- {kind}s ---")
            for r in rows[:args.limit]:
                if kind == "symbol":
                    print(f"{r['project_id']:14} {r['path']}:{r['line_start']} [{r['kind']}] {r['name']}")
                elif kind == "memory":
                    print(f"{r['project_id'] or 'GLOBAL':14} [{r['scope']}/{r['confidence']}] {r['title'][:80]}")
                else:
                    print(f"{r['project_id']:14} {r['path']}")


def cmd_module(args):
    con = connect()
    pid = _proj(con, args) or search.detect_project(con, args.name)
    row = con.execute("SELECT * FROM modules WHERE project_id=? AND (slug LIKE ? OR name LIKE ?)",
                      (pid, f"%{args.name}%", f"%{args.name}%")).fetchone()
    if not row:
        print(f"no module matching '{args.name}' in {pid}")
        return
    print(f"# {row['name']}  [{row['confidence']}]  verified@{row['verified_at_commit']}")
    print(row["body_md"])
    nf = con.execute("SELECT COUNT(*) FROM module_files WHERE module_id=?", (row["id"],)).fetchone()[0]
    print(f"\nowned files indexed: {nf}")


def cmd_impact(args):
    con = connect()
    pid = _proj(con, args)
    r = impact_fn(con, args.target, project_id=pid)
    if "error" in r:
        print(r["error"]); return
    # attach to the most recent open session for this project (telemetry)
    try:
        from cortex import session as S
        row = con.execute("""SELECT id FROM task_sessions WHERE project_id=? AND completed_at IS NULL
                             ORDER BY id DESC LIMIT 1""", (pid,)).fetchone()
        if row:
            S.record_impact(con, row["id"], args.target, r)
    except Exception:
        pass
    print(f"PROJECT: {r['project']}\nTARGETS: {', '.join(r['targets'])}")
    print(f"MODULE:  {r['module']}\nRISK:    {r['risk'].upper()}  ({'; '.join(r['reasons']) or 'isolated'})")
    if r["direct_dependents"]:
        print("\nDIRECT DEPENDENTS:")
        for d in r["direct_dependents"]:
            print(f"  {d}")
    if r["indirect_dependents"]:
        print(f"\nINDIRECT ({len(r['indirect_dependents'])}): " + ", ".join(r["indirect_dependents"][:8]) + " ...")
    if r["tests"]:
        print("\nRUN TESTS:")
        for t in r["tests"]:
            print(f"  {t}")
    if r["apis"]:
        print("\nAPIS TOUCHED:", ", ".join(r["apis"]))
    if r["db_entities"]:
        print("DB ENTITIES:", ", ".join(r["db_entities"]))
    if r["past_fixes"]:
        print("\nPAST FIXES HERE:")
        for c in r["past_fixes"]:
            print(f"  {c}")


def cmd_update(args):
    con = connect()
    from cortex.session import decay_check
    if args.project:
        stats = indexer.update_project(con, args.project)
        print(args.project, stats)
        print("decay:", decay_check(con, args.project))
    else:
        for proj in indexer.discover_projects():
            try:
                print(proj["id"], indexer.update_project(con, proj["id"]))
            except Exception as e:
                print(proj["id"], "ERROR", e)
        print("decay:", decay_check(con))


def cmd_index(args):
    con = connect()
    res = indexer.index_all(con, args.project or None)
    for pid, s in res.items():
        print(pid, s)


def cmd_tests(args):
    con = connect()
    pid = _proj(con, args) or search.detect_project(con, args.target)
    hits = search.tests_for_paths(con, pid, [args.target], limit=20)
    for h in hits:
        print(f"[{h['kind']}{' DIRECT' if h['direct'] else ''}] {h['path']}")
    if not hits:
        print(f"no test mapping found for '{args.target}' in {pid}")


def cmd_history(args):
    con = connect()
    pid = _proj(con, args) or search.detect_project(con, " ".join(args.target or []))
    if args.target:
        rows = search.recent_commits(con, pid, paths=[args.target[0]], limit=args.limit)
    else:
        rows = search.recent_commits(con, pid, limit=args.limit)
    for c in rows:
        print(f"{c['sha']} {c['date']} [{c['category']:8}] {c['subject'][:100]}")


def cmd_doctor(args):
    con = connect()
    issues = []
    for p in con.execute("SELECT * FROM projects"):
        path = pathlib.Path(p["path"])
        if not path.exists():
            issues.append(f"MISSING: project dir gone: {p['path']}")
            continue
        f = _freshness(con, p["id"])
        if f is None:
            continue
        if f["behind"] > 20:
            issues.append(f"STALE: {p['id']} brain behind by ~{f['behind']} commits -> cortex update {p['id']}")
        elif f["behind"] > 0:
            issues.append(f"DRIFT: {p['id']} behind by ~{f['behind']} commits")
        if not p["indexed_commit"] and p["git_head"]:
            issues.append(f"NOINDEX: {p['id']} git repo never committed to brain")
    try:
        con.execute("SELECT 1 FROM fts_symbols LIMIT 1").fetchone()
    except Exception as e:
        issues.append(f"FTS BROKEN: {e}")
    nmem = con.execute("SELECT COUNT(*) c FROM memories").fetchone()["c"]
    if nmem == 0:
        issues.append("EMPTY: no memories ingested -> python -m cortex.ingest_reports")
    # orphan references
    orph = con.execute("""SELECT COUNT(*) c FROM refs r WHERE dst_path IS NOT NULL AND NOT EXISTS
                          (SELECT 1 FROM files f WHERE f.project_id=r.project_id AND f.path=r.dst_path)""").fetchone()["c"]
    if orph > 200:
        issues.append(f"GRAPH: {orph} refs point at unindexed files (resolver drift)")
    # migrations applied?
    try:
        con.execute("SELECT id FROM task_sessions LIMIT 1").fetchone()
        con.execute("SELECT derived_from FROM memories LIMIT 1").fetchone()
    except Exception:
        issues.append("MIGRATIONS: learning-loop schema missing")
    # secret redaction live check
    from cortex.langs import redact
    if "hunter22" in redact("password: 'hunter22'"):
        issues.append("REDACTION: pattern check failed — do not persist until fixed")
    # MCP protocol round-trip (real subprocess, real JSON-RPC)
    try:
        import json as _json, subprocess as _sp
        srv = _sp.Popen([sys.executable, str(pathlib.Path(__file__).parent / "mcp_server.py")],
                        stdin=_sp.PIPE, stdout=_sp.PIPE, stderr=_sp.DEVNULL, text=True)
        def rpc(obj):
            srv.stdin.write(_json.dumps(obj) + "\n"); srv.stdin.flush()
            return _json.loads(srv.stdout.readline())
        hello = rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                     "params": {"protocolVersion": "2024-11-05"}})
        tools = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        call = rpc({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                    "params": {"name": "cortex_projects", "arguments": {}}})
        ok = (hello.get("result", {}).get("serverInfo", {}).get("name") == "project-cortex"
              and any(t["name"] == "cortex_context" for t in tools.get("result", {}).get("tools", []))
              and "content" in call.get("result", {}))
        srv.terminate()
        if not ok:
            issues.append("MCP: protocol round-trip failed (initialize/tools/call)")
    except Exception as e:
        issues.append(f"MCP: self-test error: {e}")
    # learning loop
    from cortex.session import decay_check, quality_report
    d = decay_check(con)
    q = quality_report(con)
    if d["obsolete_marked"] or d["uncertain_marked"]:
        issues.append(f"DECAY: {d['obsolete_marked']} episodes -> obsolete, "
                      f"{d['uncertain_marked']} -> uncertain (evidence changed)")
    if q["episodes_obsolete"] + q["episodes_uncertain"] > 0:
        print(f"info: {q['episodes_obsolete']} obsolete + {q['episodes_uncertain']} uncertain episodes; "
              f"review with `cortex episode list`")
    print("\n".join(issues) if issues else "all checks passed")


def cmd_serve(args):
    from cortex.mcp_server import serve
    serve()


BUDGETS = {"small": 2000, "normal": 4000, "deep": 8000}


def _budget(v) -> int:
    if isinstance(v, str) and v.lower() in BUDGETS:
        return BUDGETS[v.lower()]
    try:
        return max(300, min(20000, int(v)))
    except (TypeError, ValueError):
        return BUDGETS["normal"]


# ---------- learning loop ----------

def _proj(con, args) -> str | None:
    """Explicit --project > cwd detection. Exits with candidates on ambiguity."""
    from cortex.session import resolve_project
    try:
        pid = resolve_project(con, getattr(args, "project", None))
    except ValueError as e:
        print(f"AMBIGUOUS: {e}")
        raise SystemExit(2)
    return pid


def cmd_task(args):
    from cortex import session as S
    con = connect()
    try:
        _run_task(args, S, con)
    except ValueError as e:
        print("ERROR:", e)
        raise SystemExit(2)


def _run_task(args, S, con):
    if args.op == "start":
        r = S.task_start(con, args.task, project=args.project, budget=_budget(args.budget))
        if "error" in r:
            raise ValueError(r["error"])
        print(f"SESSION #{r['session_id']}  project={r['project']}  freshness={r['freshness']}  ~{r['tokens_est']} tokens")
        print(r["packet"])
        print(f"\n[hint] when done: cortex task complete --session {r['session_id']} --outcome tested "
              f"--lessons \"...\"")
    elif args.op == "complete":
        s = S.get_session(con, args.session)
        pid = s["project_id"]
        import subprocess
        sha = None
        head = subprocess.run(["git", "-C", con.execute("SELECT path FROM projects WHERE id=?", (pid,)).fetchone()[0],
                               "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", con.execute("SELECT path FROM projects WHERE id=?", (pid,)).fetchone()[0],
                                "status", "--porcelain"], capture_output=True, text=True).stdout
        if not dirty and head:
            sha = head[:12]
        r = S.task_complete(con, args.session, outcome=args.outcome,
                            problem=args.problem, root_cause=args.root_cause,
                            lessons=" ".join(args.lessons) if args.lessons else None,
                            failed_approaches=" ".join(args.failed_approach) if args.failed_approach else None,
                            solution=" ".join(args.solution) if getattr(args, "solution", None) else None,
                            tests_run=args.tests_run.split(",") if args.tests_run else None,
                            commit_sha=sha)
        print(json.dumps({k: v for k, v in r.items() if k != "evidence"}, indent=1))
        ev = r.get("evidence") or {}
        for k, v in ev.items():
            if v:
                print(f"{k}: {', '.join(map(str, v[:8]))}")
        if not sha:
            print("note: working tree dirty / no explicit commit — episode recorded without commit link")
    elif args.op == "list":
        for s in con.execute("SELECT id,project_id,outcome,episode_id,substr(task,1,70) t,started_at FROM task_sessions ORDER BY id DESC LIMIT 20"):
            print(f"#{s['id']:4} {s['project_id'] or '?':14} {s['outcome'] or 'open':12} ep:{s['episode_id'] or '-':5} {s['t']}")
    elif args.op == "show":
        s = S.get_session(con, args.session)
        for k in s.keys():
            v = s[k]
            if v not in (None, ""):
                print(f"{k}: {str(v)[:300]}")
        if s["episode_id"]:
            ep = con.execute("SELECT * FROM episodes WHERE id=?", (s["episode_id"],)).fetchone()
            print("\n--- EPISODE ---")
            for k in ("task", "problem", "root_cause", "solution", "failed_approaches",
                      "lessons", "commit_sha", "status", "outcome", "confidence"):
                if ep[k]:
                    print(f"{k}: {ep[k][:400]}")


def cmd_episode(args):
    from cortex import session as S
    con = connect()
    if args.op == "list":
        for e in con.execute("SELECT id,project_id,status,outcome,confidence,substr(task,1,60) t FROM episodes ORDER BY id DESC LIMIT 30"):
            print(f"#{e['id']:4} {e['project_id'] or 'GLOBAL':14} {e['status']:10} {e['outcome'] or '-':12} {e['confidence']:16} {e['t']}")
    elif args.op == "supersede":
        S.supersede_episode(con, args.id, args.by, status=args.status)
        print(f"episode #{args.id} -> {args.status}" + (f" (by #{args.by})" if args.by else ""))
    elif args.op == "promote":
        mid = S.promote_episode(con, args.id, scope=args.scope)
        print(f"promoted to memory #{mid}" if mid else "not promoted (no lessons or duplicate knowledge)")


def cmd_quality(args):
    from cortex.session import quality_report
    q = quality_report(connect())
    print(f"Cortex Quality")
    print(f"sessions started/completed : {q['sessions_started']} / {q['sessions_completed']}")
    print(f"episodes active/total      : {q['episodes_active']} / {q['episodes_total']}"
          f"  (failed-lesson {q['episodes_failed_lessons']}, uncertain {q['episodes_uncertain']}, obsolete {q['episodes_obsolete']})")
    print(f"generated memories         : {q['memories_generated']}   stale memories: {q['stale_memories']}")
    fmt = lambda v: f"{v:.0%}" if isinstance(v, float) else "n/a"
    print(f"primary-file hit rate      : {fmt(q['primary_file_hit_rate'])}   suggestion recall: {fmt(q['suggestion_recall'])}")
    print(f"test-recommendation hit    : {fmt(q['test_hit_rate'])}")


def main():
    ap = argparse.ArgumentParser(prog="cortex", description="Project Cortex — engineering brain")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("projects").set_defaults(fn=cmd_projects)
    sp = sub.add_parser("status"); sp.add_argument("task", nargs="?"); sp.add_argument("--project"); sp.set_defaults(fn=cmd_status)
    sp = sub.add_parser("context"); sp.add_argument("task"); sp.add_argument("--project"); sp.add_argument("--budget", default=4000); sp.add_argument("--all", action="store_true"); sp.set_defaults(fn=cmd_context)
    sp = sub.add_parser("search"); sp.add_argument("query"); sp.add_argument("--project"); sp.add_argument("--limit", type=int, default=8); sp.set_defaults(fn=cmd_search)
    sp = sub.add_parser("module"); sp.add_argument("name"); sp.add_argument("--project"); sp.set_defaults(fn=cmd_module)
    sp = sub.add_parser("impact"); sp.add_argument("target"); sp.add_argument("--project"); sp.set_defaults(fn=cmd_impact)
    sp = sub.add_parser("update"); sp.add_argument("project", nargs="?"); sp.set_defaults(fn=cmd_update)
    sp = sub.add_parser("index"); sp.add_argument("project", nargs="*"); sp.set_defaults(fn=cmd_index)
    sp = sub.add_parser("tests"); sp.add_argument("target"); sp.add_argument("--project"); sp.set_defaults(fn=cmd_tests)
    sp = sub.add_parser("history"); sp.add_argument("target", nargs="*"); sp.add_argument("--project"); sp.add_argument("--limit", type=int, default=15); sp.set_defaults(fn=cmd_history)
    sub.add_parser("doctor").set_defaults(fn=cmd_doctor)
    sub.add_parser("serve").set_defaults(fn=cmd_serve)
    sp = sub.add_parser("quality").set_defaults(fn=cmd_quality)
    sp = sub.add_parser("task"); tsub = sp.add_subparsers(dest="op", required=True)
    ts = tsub.add_parser("start"); ts.add_argument("task"); ts.add_argument("--project"); ts.add_argument("--budget", default=3000); ts.set_defaults(fn=cmd_task)
    tc = tsub.add_parser("complete"); tc.add_argument("--session", type=int, required=True); tc.add_argument("--outcome", default="implemented", choices=["implemented", "tested", "verified", "failed", "partial", "abandoned"]); tc.add_argument("--problem"); tc.add_argument("--root-cause", dest="root_cause"); tc.add_argument("--lessons", nargs="+"); tc.add_argument("--failed-approach", dest="failed_approach", nargs="+"); tc.add_argument("--solution", nargs="+"); tc.add_argument("--tests-run", dest="tests_run"); tc.add_argument("--project"); tc.set_defaults(fn=cmd_task)
    tl = tsub.add_parser("list"); tl.set_defaults(fn=cmd_task)
    tw = tsub.add_parser("show"); tw.add_argument("session", type=int); tw.set_defaults(fn=cmd_task)
    sp = sub.add_parser("episode"); esub = sp.add_subparsers(dest="op", required=True)
    el = esub.add_parser("list"); el.set_defaults(fn=cmd_episode)
    esu = esub.add_parser("supersede"); esu.add_argument("id", type=int); esu.add_argument("--by", type=int); esu.add_argument("--status", default="superseded", choices=["superseded", "obsolete", "uncertain", "active"]); esu.set_defaults(fn=cmd_episode)
    epr = esub.add_parser("promote"); epr.add_argument("id", type=int); epr.add_argument("--scope", choices=["global", "module", "pitfall"]); epr.set_defaults(fn=cmd_episode)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
