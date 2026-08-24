"""Zero-dependency MCP server (JSON-RPC 2.0 over stdio)."""
from __future__ import annotations
import json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from cortex.db import connect
from cortex import search
from cortex.contextpack import context as ctx_fn, impact as impact_fn
from cortex.indexer import update_project

CON = connect()


def tool_context(args):
    r = ctx_fn(CON, args["task"], project_id=args.get("project"),
               budget=int(args.get("budget", 4000)))
    return [{"type": "text", "text": r.get("packet") or r.get("error", "")}]


def tool_search(args):
    q, pid = args["query"], args.get("project")
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
    r = impact_fn(CON, args["target"], project_id=args.get("project"))
    return [{"type": "text", "text": json.dumps(r, indent=1)}]


def tool_module(args):
    pid = args.get("project") or search.detect_project(CON, args["name"])
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
    pid = args.get("project") or search.detect_project(CON, args["path"])
    cl = search.callers_of(CON, pid, args["path"], args.get("symbol"))
    imps = search.importers_of(CON, pid, args["path"])
    lines = [f"calls into {args['path']}:" ] + [f"  {c}" for c in cl] + ["imports it:"] + [f"  {i}" for i in imps]
    return [{"type": "text", "text": "\n".join(lines)}]


def tool_tests(args):
    pid = args.get("project") or search.detect_project(CON, args["target"])
    hits = search.tests_for_paths(CON, pid, [args["target"]], limit=15)
    return [{"type": "text", "text": "\n".join(
        f"[{h['kind']}{' DIRECT' if h['direct'] else ''}] {h['path']}" for h in hits) or "no mapped tests"}]


def tool_projects(args):
    rows = []
    for p in CON.execute("SELECT id,name,path,kind,languages,indexed_commit,git_head,dirty_files FROM projects ORDER BY id"):
        fresh = "fresh" if p["git_head"] == p["indexed_commit"] else f"behind/dirty({p['dirty_files']})"
        rows.append(f"{p['id']:16} {p['kind'] or '':10} {fresh:20} {p['languages']}")
    return [{"type": "text", "text": "\n".join(rows)}]


def tool_status(args):
    pid = args.get("project")
    if not pid:
        n = CON.execute("SELECT COUNT(*) c FROM projects").fetchone()["c"]
        return [{"type": "text", "text": f"cortex: {n} projects indexed. Pass a project for details."}]
    p = CON.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    def c(sql):
        return CON.execute(sql, (pid,)).fetchone()[0]
    stale_mem = c("SELECT COUNT(*) FROM memories WHERE project_id=? AND stale=1")
    return [{"type": "text", "text":
             f"{p['name']} ({pid})\nHEAD {(p['git_head'] or '')[:12]} | indexed@{(p['indexed_commit'] or '')[:12]}\n"
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
    pid = args.get("project") or search.detect_project(CON, args.get("path") or "")
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
    "cortex_context": ("Budgeted engineering context packet for a natural-language task.",
       {"task": {"type": "string"}, "project": {"type": "string"}, "budget": {"type": "number"}}, tool_context, ["task"]),
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
    method = req.get("method", "")
    rid = req.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "project-cortex", "version": "0.1.0"}}}
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
        name = req["params"]["name"]
        fn = TOOLS.get(name)
        if not fn:
            return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32602, "message": f"unknown tool {name}"}}
        try:
            result = fn[2](req["params"].get("arguments", {}))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": result}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": f"error: {e}"}], "isError": True}}
    if method.startswith("notifications/"):
        return {}
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"unknown method {method}"}}


def serve():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(req)
        if resp:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    serve()
