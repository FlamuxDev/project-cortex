"""Zero-dependency MCP server (JSON-RPC 2.0 over stdio)."""
from __future__ import annotations
import atexit, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from cortex.db import code_root, connect
from cortex import search
from cortex.contextpack import context as ctx_fn, impact as impact_fn
from cortex.indexer import update_project
from cortex import session as S
from cortex import __version__

CON = connect()
atexit.register(CON.close)


def _pid(args, hint: str | None = None):
    """Resolve explicit project/cwd, then an explicit project name, then server cwd."""
    try:
        if args.get("project"):
            return S.resolve_project(CON, args["project"])
        if args.get("cwd"):
            return S.resolve_project(CON, cwd=args["cwd"])
        named = search.detect_named_project(CON, hint or "")
        return named or S.resolve_project(CON)
    except ValueError as e:
        raise ValueError(str(e))


def tool_context(args):
    r = ctx_fn(CON, args["task"], project_id=_pid(args, args["task"]),
               budget=int(args.get("budget", 4000)))
    return [{"type": "text", "text": r.get("packet") or r.get("error", "")}]


def tool_task_start(args):
    r = S.task_start(CON, args["task"], project=_pid(args, args["task"]),
                     budget=int(args.get("budget", 3000)))
    if "error" in r:
        return [{"type": "text", "text": f"error: {r['error']}"}]
    packet = r.pop("packet")
    head = [f"SESSION #{r['session_id']} | project={r['project']} | freshness={r['freshness']} "
            f"| ~{r['tokens_est']} tokens", "",
            "When done, call cortex_task_complete with this session id and durable lessons.", ""]
    return [{"type": "text", "text": "\n".join(head) + packet}]


def tool_search(args):
    q, pid = args["query"], _pid(args, args["query"])
    out = []
    for kind, fn in [("symbol", search.search_symbols), ("memory", search.search_memories),
                     ("file", search.search_files)]:
        for r in fn(CON, pid, q, limit=6)[:6]:
            if kind == "symbol":
                out.append(f"{r['project_id']} {r['path']}:{r['line_start']} [{r['kind']}] {r['name']}")
            elif kind == "memory":
                out.append(f"{r['project_id'] or 'GLOBAL'} [{r['scope']}/{r['confidence']}{' STALE' if r['stale'] else ''}] {r['title']}: {r['body_md'][:200]}")
            else:
                out.append(f"{r['project_id']} {r['path']}")
    return [{"type": "text", "text": "\n".join(out) or "no results"}]


def tool_impact(args):
    r = impact_fn(CON, args["target"], project_id=_pid(args, args["target"]))
    sid = args.get("session")
    if "error" not in r and sid:
        try:
            S.record_impact(CON, int(sid), args["target"], r)
        except Exception:
            pass
    elif "error" not in r:
        row = CON.execute("""SELECT id FROM task_sessions WHERE project_id=? AND completed_at IS NULL
                             ORDER BY id DESC LIMIT 1""", (r.get("project"),)).fetchone()
        if row:
            try:
                S.record_impact(CON, row["id"], args["target"], r)
            except Exception:
                pass
    return [{"type": "text", "text": json.dumps(r, indent=1)}]


def tool_task_complete(args):
    try:
        r = S.task_complete(CON, int(args["session_id"]),
                            outcome=args.get("outcome", "implemented"),
                            problem=args.get("problem"),
                            root_cause=args.get("root_cause"),
                            lessons=args.get("lessons"),
                            failed_approaches=args.get("failed_approaches"),
                            tests_run=args.get("tests_run"),
                            commit_sha=args.get("commit_sha"))
    except ValueError as e:
        return [{"type": "text", "text": f"error: {e}"}]
    out = {k: v for k, v in r.items() if k != "evidence"}
    ev = r.get("evidence") or {}
    lines = [json.dumps(out, indent=1)]
    for k, v in ev.items():
        if v:
            lines.append(f"{k}: {', '.join(map(str, v[:8]))}")
    return [{"type": "text", "text": "\n".join(lines)}]


def tool_quality(args):
    q = S.quality_report(CON)
    d = S.decay_check(CON)
    q.update(d)
    return [{"type": "text", "text": json.dumps(q, indent=1)}]


def tool_module(args):
    pid = _pid(args, args["name"])
    rows = CON.execute("SELECT * FROM modules WHERE project_id=? AND (slug LIKE ? OR name LIKE ?)",
                       (pid, f"%{args['name']}%", f"%{args['name']}%")).fetchall()
    texts = [f"# {m['name']} [{m['confidence']}] verified@{m['verified_at_commit']}\n{m['body_md']}" for m in rows]
    return [{"type": "text", "text": "\n\n---\n\n".join(texts) or f"no module '{args['name']}' in {pid}"}]


def tool_symbol(args):
    name = args["name"]
    pid = args.get("project")
    sql = """SELECT project_id,path,name,kind,line_start,line_end,signature,parent FROM symbols
             WHERE name=? """
    args_l = [name]
    if pid:
        sql += "AND project_id=? "
        args_l.append(pid)
    rows = CON.execute(sql + "ORDER BY importance DESC LIMIT ?", (*args_l, 10)).fetchall()
    out = [f"{r['project_id']} {r['path']}:{r['line_start']}-{r['line_end']} [{r['kind']}{' of '+r['parent'] if r['parent'] else ''}] {r['signature'][:120]}" for r in rows]
    return [{"type": "text", "text": "\n".join(out) or f"symbol '{name}' not found"}]


def tool_references(args):
    name, pid = args["name"], args.get("project")
    sql = """SELECT DISTINCT src_path FROM refs WHERE dst_name LIKE ? AND kind IN ('call','use')"""
    args_l = [f"%{name}"]
    if pid:
        sql += " AND project_id=?"
        args_l.append(pid)
    rows = CON.execute(sql + " LIMIT 25", args_l).fetchall()
    return [{"type": "text", "text": "\n".join(f"called/referenced in: {r['src_path']}" for r in rows) or "no references found"}]


def tool_callers(args):
    pid = _pid(args, args["path"])
    cl = search.callers_of(CON, pid, args["path"], args.get("symbol"))
    imps = search.importers_of(CON, pid, args["path"])
    lines = [f"calls into {args['path']}:" ] + [f"  {c}" for c in cl] + ["imports it:"] + [f"  {i}" for i in imps]
    return [{"type": "text", "text": "\n".join(lines)}]


def tool_tests(args):
    pid = _pid(args, args["target"])
    hits = search.tests_for_paths(CON, pid, [args["target"]], limit=15)
    return [{"type": "text", "text": "\n".join(
        f"[{h['kind']}{' DIRECT' if h['direct'] else ''}] {h['path']}" for h in hits) or "no mapped tests"}]


def tool_projects(args):
    rows = []
    for p in CON.execute("SELECT * FROM projects ORDER BY id"):
        root = pathlib.Path(code_root(p))
        if not root.is_dir():
            state = "path-gone"
        else:
            info = S.live_git(str(root), p["indexed_commit"])
            state = S.freshness_status(info)
            if info["dirty"]:
                state += f"({info['dirty']})"
        rows.append(f"{p['id']:16} {p['kind'] or '':10} {state:20} {p['languages']}")
    return [{"type": "text", "text": "\n".join(rows)}]


def tool_status(args):
    pid = args.get("project")
    if not pid:
        n = CON.execute("SELECT COUNT(*) c FROM projects").fetchone()["c"]
        return [{"type": "text", "text": f"cortex: {n} projects indexed. Pass a project for details."}]
    p = CON.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    if not p:
        return [{"type": "text", "text": f"error: unknown project '{pid}'"}]
    def c(sql):
        return CON.execute(sql, (pid,)).fetchone()[0]
    stale_mem = c("SELECT COUNT(*) FROM memories WHERE project_id=? AND stale=1")
    root = pathlib.Path(code_root(p))
    if not root.is_dir():
        state = "path-gone"
        gitinfo = {"head": "", "indexed": (p["indexed_commit"] or "")[:12]}
    else:
        gitinfo = S.live_git(str(root), p["indexed_commit"])
        state = S.freshness_status(gitinfo)
    return [{"type": "text", "text":
             f"{p['name']} ({pid})\nPATH {root}\nSTATE {state}\n"
             f"HEAD {gitinfo['head']} | indexed@{gitinfo['indexed']}\n"
             f"files={c('SELECT COUNT(*) FROM files WHERE project_id=?')} symbols={c('SELECT COUNT(*) FROM symbols WHERE project_id=?')} "
             f"modules={c('SELECT COUNT(*) FROM modules WHERE project_id=?')} flows={c('SELECT COUNT(*) FROM flows WHERE project_id=?')} "
             f"apis={c('SELECT COUNT(*) FROM apis WHERE project_id=?')} tests={c('SELECT COUNT(*) FROM tests WHERE project_id=?')} "
             f"stale_memories={stale_mem}\nlast indexed: {p['last_indexed_at']}"}]


def tool_update(args):
    if not args.get("project"):
        done = []
        for p in CON.execute("SELECT id FROM projects"):
            try:
                done.append(f"{p['id']}: {update_project(CON, p['id'])}")
            except Exception as e:
                done.append(f"{p['id']}: ERROR {e}")
        return [{"type": "text", "text": "\n".join(done)}]
    stats = update_project(CON, args["project"])
    return [{"type": "text", "text": json.dumps(stats)}]


def tool_history(args):
    pid = _pid(args, args.get("path") or "")
    paths = [args["path"]] if args.get("path") else None
    rows = search.recent_commits(CON, pid, paths=paths, limit=int(args.get("limit", 12)),
                                 category=args.get("category"))
    return [{"type": "text", "text": "\n".join(f"{c['sha']} {c['date']} [{c['category']}] {c['subject']}" for c in rows)}]


def tool_changed_since(args):
    pid = args["project"]
    since_sha = args["since"]
    rows = CON.execute("""SELECT DISTINCT cf.path FROM commits c JOIN commit_files cf ON
                          cf.project_id=c.project_id AND cf.sha=c.sha
                          WHERE c.project_id=? AND c.date >= COALESCE(
                            (SELECT date FROM commits WHERE project_id=? AND sha LIKE ?),'1970-01-01')
                          LIMIT 100""", (pid, pid, since_sha[:12] + "%")).fetchall()
    return [{"type": "text", "text": "\n".join(r["path"] for r in rows) or "nothing changed since that commit"}]


TOOLS = {
    "cortex_task_start": ("Start a tracked task session: resolves project from explicit project/cwd, checks freshness, returns full context packet (module/files/symbols/tests/past lessons). Call this FIRST for any non-trivial task.",
       {"task": {"type": "string"}, "project": {"type": "string"}, "cwd": {"type": "string"}, "budget": {"type": "number"}}, tool_task_start, ["task"]),
    "cortex_task_complete": ("Close a task session: gathers git evidence, computes retrieval precision metrics, stores a durable episode. Pass lessons=root-cause/invariant knowledge worth remembering; outcome in implemented|tested|verified|failed|partial|abandoned.",
       {"session_id": {"type": "number"}, "outcome": {"type": "string"}, "problem": {"type": "string"},
        "root_cause": {"type": "string"}, "lessons": {"type": "string"},
        "failed_approaches": {"type": "string"}, "tests_run": {"type": "array", "items": {"type": "string"}},
        "commit_sha": {"type": "string"}}, tool_task_complete, ["session_id"]),
    "cortex_quality": ("Learning-loop health: session/episode counts, hit rates, decay flags.", {}, tool_quality, []),
    "cortex_context": ("Budgeted engineering context packet for a natural-language task (no session tracking).",
       {"task": {"type": "string"}, "project": {"type": "string"}, "cwd": {"type": "string"}, "budget": {"type": "number"}}, tool_context, ["task"]),
    "cortex_search": ("Hybrid lexical+graph search across code, symbols and knowledge.",
       {"query": {"type": "string"}, "project": {"type": "string"}}, tool_search, ["query"]),
    "cortex_impact": ("Blast-radius estimate for changing a file/symbol/feature.",
       {"target": {"type": "string"}, "project": {"type": "string"}}, tool_impact, ["target"]),
    "cortex_module": ("Module memory: purpose, files, invariants, pitfalls.",
       {"name": {"type": "string"}, "project": {"type": "string"}}, tool_module, ["name"]),
    "cortex_symbol": ("Find symbol definitions by exact name.",
       {"name": {"type": "string"}, "project": {"type": "string"}}, tool_symbol, ["name"]),
    "cortex_references": ("Files referencing/calling a named symbol.",
       {"name": {"type": "string"}, "project": {"type": "string"}}, tool_references, ["name"]),
    "cortex_callers": ("Callers and importers of a file (optionally a symbol within it).",
       {"path": {"type": "string"}, "symbol": {"type": "string"}, "project": {"type": "string"}}, tool_callers, ["path"]),
    "cortex_tests": ("Tests covering a file/target.",
       {"target": {"type": "string"}, "project": {"type": "string"}}, tool_tests, ["target"]),
    "cortex_projects": ("List all indexed projects.", {}, tool_projects, []),
    "cortex_status": ("Per-project index status/freshness.", {"project": {"type": "string"}}, tool_status, []),
    "cortex_update": ("Incrementally re-index changed files.", {"project": {"type": "string"}}, tool_update, []),
    "cortex_history": ("Recent commits, optionally filtered by path/category.",
       {"project": {"type": "string"}, "path": {"type": "string"}, "category": {"type": "string"}, "limit": {"type": "number"}},
       tool_history, []),
    "cortex_changed_since": ("Files changed in repo since a given commit sha (vs brain state).",
       {"project": {"type": "string"}, "since": {"type": "string"}}, tool_changed_since, ["project", "since"]),
}


def handle(req: dict) -> dict:
    if not isinstance(req, dict):
        return {"jsonrpc": "2.0", "id": None,
                "error": {"code": -32600, "message": "invalid request: expected object"}}
    method = req.get("method", "")
    rid = req.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "project-cortex", "version": __version__}}}
    if method == "notifications/initialized":
        return {}
    if method == "tools/list":
        tools_out = []
        for n, (d, props, _, required) in TOOLS.items():
            schema = {"type": "object", "properties": props}
            if required:
                schema["required"] = required
            tools_out.append({"name": n, "description": d, "inputSchema": schema})
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": tools_out}}
    if method == "tools/call":
        name = req.get("params", {}).get("name")
        fn = TOOLS.get(name)
        if not fn:
            return {"jsonrpc": "2.0", "id": rid,
                    "error": {"code": -32602, "message": f"unknown tool {name}"}}
        try:
            result = fn[2](req["params"].get("arguments", {}))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": result}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": f"error: {e}"}], "isError": True}}
    if method.startswith("notifications/"):
        return {}
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"unknown method {method}"}}


def serve():
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except json.JSONDecodeError:
                resp = {"jsonrpc": "2.0", "id": None,
                        "error": {"code": -32700, "message": "parse error"}}
            else:
                try:
                    resp = handle(req)
                except Exception as e:  # one bad frame must never kill the server
                    rid = req.get("id") if isinstance(req, dict) else None
                    resp = {"jsonrpc": "2.0", "id": rid,
                            "error": {"code": -32603, "message": f"internal error: {e}"}}
            if resp:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        CON.close()


if __name__ == "__main__":
    serve()
