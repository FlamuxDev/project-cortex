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
    print(context_text(con, args.task, project_id=args.project,
                       budget=args.budget))


def cmd_search(args):
    con = connect()
    pid = args.project or search.detect_project(con, args.query)
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
    pid = args.project or search.detect_project(con, args.name)
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
    r = impact_fn(con, args.target, project_id=args.project)
    if "error" in r:
        print(r["error"]); return
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
    if args.project:
        stats = indexer.update_project(con, args.project)
        print(args.project, stats)
    else:
        for proj in indexer.discover_projects():
            try:
                print(proj["id"], indexer.update_project(con, proj["id"]))
            except Exception as e:
                print(proj["id"], "ERROR", e)


def cmd_index(args):
    con = connect()
    res = indexer.index_all(con, args.project or None)
    for pid, s in res.items():
        print(pid, s)


def cmd_tests(args):
    con = connect()
    pid = args.project or search.detect_project(con, args.target)
    hits = search.tests_for_paths(con, pid, [args.target], limit=20)
    for h in hits:
        print(f"[{h['kind']}{' DIRECT' if h['direct'] else ''}] {h['path']}")
    if not hits:
        print(f"no test mapping found for '{args.target}' in {pid}")


def cmd_history(args):
    con = connect()
    pid = args.project or search.detect_project(con, " ".join(args.target or []))
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
    print("\n".join(issues) if issues else "all checks passed")


def cmd_serve(args):
    from cortex.mcp_server import serve
    serve()


def main():
    ap = argparse.ArgumentParser(prog="cortex", description="Project Cortex — engineering brain")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("projects").set_defaults(fn=cmd_projects)
    sp = sub.add_parser("status"); sp.add_argument("task", nargs="?"); sp.add_argument("--project"); sp.set_defaults(fn=cmd_status)
    sp = sub.add_parser("context"); sp.add_argument("task"); sp.add_argument("--project"); sp.add_argument("--budget", type=int, default=4000); sp.add_argument("--all", action="store_true"); sp.set_defaults(fn=cmd_context)
    sp = sub.add_parser("search"); sp.add_argument("query"); sp.add_argument("--project"); sp.add_argument("--limit", type=int, default=8); sp.set_defaults(fn=cmd_search)
    sp = sub.add_parser("module"); sp.add_argument("name"); sp.add_argument("--project"); sp.set_defaults(fn=cmd_module)
    sp = sub.add_parser("impact"); sp.add_argument("target"); sp.add_argument("--project"); sp.set_defaults(fn=cmd_impact)
    sp = sub.add_parser("update"); sp.add_argument("project", nargs="?"); sp.set_defaults(fn=cmd_update)
    sp = sub.add_parser("index"); sp.add_argument("project", nargs="*"); sp.set_defaults(fn=cmd_index)
    sp = sub.add_parser("tests"); sp.add_argument("target"); sp.add_argument("--project"); sp.set_defaults(fn=cmd_tests)
    sp = sub.add_parser("history"); sp.add_argument("target", nargs="*"); sp.add_argument("--project"); sp.add_argument("--limit", type=int, default=15); sp.set_defaults(fn=cmd_history)
    sub.add_parser("doctor").set_defaults(fn=cmd_doctor)
    sub.add_parser("serve").set_defaults(fn=cmd_serve)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
