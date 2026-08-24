"""Per-language symbol/reference/route/table extraction.

Every extractor returns FileResult dicts:
{symbols: [{name,kind,parent,line_start,line_end,signature,doc,exported}],
 refs: [{dst_name,kind,line}], routes: [{method,route,handler_symbol,auth}],
 tables: [{name,kind}]}
"""
from __future__ import annotations
import re, ast as pyast

# ---------------------------------------------------------------- data shapes
def new_result(path):
    return {"path": path, "symbols": [], "refs": [], "routes": [], "tables": []}


def sym(name, kind, ls=0, le=0, sig=None, doc=None, parent=None, exported=0):
    return {"name": name, "kind": kind, "parent": parent, "line_start": ls,
            "line_end": le, "signature": sig, "doc": doc, "exported": exported}


HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "all", "use"}

# ---------------------------------------------------------------- TypeScript / JavaScript
_TS_CACHE = {}

def _ts_parser(lang: str):
    from tree_sitter import Language, Parser
    if lang not in _TS_CACHE:
        import tree_sitter_typescript as tsts
        import tree_sitter_javascript as tsjs
        ptr = {"ts": tsts.language_typescript, "tsx": tsts.language_tsx,
               "js": tsjs.language, "jsx": tsjs.language}[lang]
        _TS_CACHE[lang] = Parser(Language(ptr()))
    return _TS_CACHE[lang]


def _node_text(node, src):
    return src[node.start_byte:node.end_byte].decode("utf8", "replace")


def _walk(node, kinds, stop_at=None):
    out = []
    stack = [node]
    while stack:
        n = stack.pop()
        if stop_at and n.type in stop_at and n is not node:
            continue
        if n.type in kinds:
            out.append(n)
        stack.extend(n.children)
    return out


def _sig_of(node, src, limit=120):
    text = " ".join(_node_text(node, src).split())
    return text[:limit]


def extract_ts(src_bytes: bytes, lang: str, path: str) -> dict:
    res = new_result(path)
    parser = _ts_parser(lang)
    tree = parser.parse(src_bytes)
    root = tree.root_node
    src = src_bytes

    imported_names = {}   # local name -> module specifier (+ optional imported symbol)
    for imp in _walk(root, {"import_statement", "import_from_statement"}):
        mod = None
        for c in imp.children:
            if c.type == "string":
                mod = _node_text(c, src).strip("'\"")
        if mod is None:
            continue
        res["refs"].append({"dst_name": mod, "kind": "import", "line": imp.start_point[0] + 1})
        for ident in _walk(imp, {"identifier", "shorthand_property_identifier_pattern", "namespace_import", "import_specifier"}):
            if ident.type == "import_specifier":
                name_node = ident.children[0] if ident.children else None
                if name_node:
                    imported_names[_node_text(name_node, src)] = mod
            elif ident.type == "namespace_import":
                nxt = ident.next_sibling
                if nxt is not None:
                    imported_names[_node_text(nxt, src)] = mod
            else:
                imported_names[_node_text(ident, src)] = mod

    def add_call_refs(call_node):
        fn = call_node.child_by_field_name("function")
        if fn is None:
            return
        fname = _node_text(fn, src)
        base = fname.split(".")[0]
        if base in imported_names and "." in fname:
            tgt_mod = imported_names[base]
            res["refs"].append({"dst_name": f"{tgt_mod}:{fname}", "dst_path_hint": tgt_mod,
                                "kind": "call", "line": call_node.start_point[0] + 1})
        elif base in imported_names:
            res["refs"].append({"dst_name": f"{imported_names[base]}::{fname}", "dst_path_hint": imported_names[base],
                                "kind": "call", "line": call_node.start_point[0] + 1})

    # declarations
    for cls in _walk(root, {"class_declaration", "class"}):
        nm = cls.child_by_field_name("name")
        if nm is None:
            continue
        name = _node_text(nm, src)
        exported = cls.parent and cls.parent.type == "export_statement"
        res["symbols"].append(sym(name, "class", cls.start_point[0] + 1, cls.end_point[0],
                                  _sig_of(cls, src), parent=None, exported=int(bool(exported))))
        for m in _walk(cls.child_by_field_name("body"), {"method_definition"}):
            mn = m.child_by_field_name("name")
            if mn is not None:
                res["symbols"].append(sym(_node_text(mn, src), "method", m.start_point[0] + 1,
                                          m.end_point[0], _sig_of(m, src), parent=name))
        # NestJS-style decorators: @Controller("base") class + @Get("sub") methods
        ctrl_base = ""
        for deco in _walk(cls, {"decorator"}, stop_at={"method_definition"}):
            dtext = _node_text(deco, src)
            mc = re.match(r"@Controller\s*(?:\(\s*['\"]([^'\"]*)['\"])?", dtext)
            if mc:
                ctrl_base = (mc.group(1) or "").strip("/")
        for deco in _walk(cls, {"decorator"}):
            dtext = _node_text(deco, src)
            m2 = re.match(r"@(\w+)\s*(?:\(\s*['\"]([^'\"]*)['\"]\s*\))?", dtext)
            if not m2:
                continue
            meth, sub = m2.group(1), (m2.group(2) or "").strip("/")
            if meth.upper() in {x.upper() for x in HTTP_METHODS - {"use", "all", "options", "head"}}:
                route = "/".join(x for x in (ctrl_base, sub) if x)
                sib = deco.parent
                handler = None
                while sib is not None and sib.type != "method_definition":
                    sib = sib.next_named_sibling
                if sib is not None:
                    hname = sib.child_by_field_name("name")
                    handler = _node_text(hname, src) if hname else None
                res["routes"].append({"method": meth.upper(), "route": "/" + route if route else "/",
                                      "handler_symbol": handler, "auth": None})

    for iface in _walk(root, {"interface_declaration"}):
        nm = iface.child_by_field_name("name")
        if nm is not None:
            res["symbols"].append(sym(_node_text(nm, src), "interface", iface.start_point[0] + 1,
                                      iface.end_point[0], _sig_of(iface, src),
                                      exported=int(iface.parent and iface.parent.type == "export_statement")))
    for ta in _walk(root, {"type_alias_declaration"}):
        nm = ta.child_by_field_name("name")
        if nm is not None:
            res["symbols"].append(sym(_node_text(nm, src), "type", ta.start_point[0] + 1,
                                      ta.end_point[0], _sig_of(ta, src)[:80],
                                      exported=int(ta.parent and ta.parent.type == "export_statement")))
    for en in _walk(root, {"enum_declaration"}):
        nm = en.child_by_field_name("name")
        if nm is not None:
            res["symbols"].append(sym(_node_text(nm, src), "enum", en.start_point[0] + 1,
                                      en.end_point[0], exported=int(en.parent and en.parent.type == "export_statement")))

    # functions + exported const arrow functions (components etc.)
    for fd in _walk(root, {"function_declaration", "generator_function_declaration"}):
        nm = fd.child_by_field_name("name")
        if nm is None:
            continue
        exported = fd.parent and fd.parent.type == "export_statement"
        res["symbols"].append(sym(_node_text(nm, src), "function", fd.start_point[0] + 1, fd.end_point[0],
                                  _sig_of(fd, src), exported=int(bool(exported))))

    for vd in _walk(root, {"lexical_declaration", "variable_declaration"}):
        exported = vd.parent and vd.parent.type == "export_statement"
        for decl in _walk(vd, {"variable_declarator"}):
            nm = decl.child_by_field_name("name")
            val = decl.child_by_field_name("value")
            if nm is None or val is None:
                continue
            if val.type in {"arrow_function", "function_expression", "function"}:
                name = _node_text(nm, src)
                kind = "component" if name[:1].isupper() else "function"
                res["symbols"].append(sym(name, kind, decl.start_point[0] + 1, vd.end_point[0],
                                          _sig_of(decl, src), exported=int(bool(exported))))

    # calls: record edges only for interesting names (imports resolved later)
    for call in _walk(root, {"call_expression"}):
        fn = call.child_by_field_name("function")
        args = call.child_by_field_name("arguments")
        if fn is None or args is None or not args.named_children:
            continue
        fname = _node_text(fn, src)
        add_call_refs(call)
        # REST routes: app.get("/x", handler) / router.post(...)
        parts = fname.split(".")
        if len(parts) == 2 and parts[1].lower() in HTTP_METHODS:
            a0 = args.named_children[0]
            if a0.type == "string":
                route = _node_text(a0, src).strip("'\"`")
                handler = _node_text(args.named_children[-1], src)[:60] if len(args.named_children) > 1 else None
                res["routes"].append({"method": parts[1].upper(), "route": route,
                                      "handler_symbol": handler, "auth": None})
        # drizzle/pg tables: pgTable("users", {...}) / sqliteTable(...)
        if re.match(r"^\w*[Tt]able$", parts[-1]) and len(args.named_children) >= 1:
            a0 = args.named_children[0]
            if a0.type == "string":
                res["tables"].append({"name": _node_text(a0, src).strip("'\"`"), "kind": "table"})

    # z.object schemas / jsonb types skipped intentionally (noise)
    return res


# ---------------------------------------------------------------- Python
_PY_ROUTE_DECOS = re.compile(r"^(?:\w+\.)?(get|post|put|patch|delete|head|options)$", re.I)

class _PyVisitor(pyast.NodeVisitor):
    def __init__(self, res, src_lines):
        self.res = res
        self.lines = src_lines
        self.class_stack = []

    def _doc(self, node):
        body = getattr(node, "body", [])
        if body and isinstance(body[0], pyast.Expr) and isinstance(body[0].value, pyast.Constant) \
           and isinstance(body[0].value.value, str):
            return body[0].value.value[:300]
        return None

    def _route(self, node, name):
        for dec in node.decorator_list:
            target = dec.func if isinstance(dec, pyast.Call) else dec
            if isinstance(target, pyast.Attribute) and _PY_ROUTE_DECOS.match(target.attr):
                method = target.attr.upper()
                route = ""
                if isinstance(dec, pyast.Call) and dec.args and isinstance(dec.args[0], pyast.Constant):
                    route = str(dec.args[0].value)
                self.res["routes"].append({"method": method, "route": route, "handler_symbol": name, "auth": None})
            elif isinstance(target, pyast.Name) and target.id in {"app", "router"}:
                pass

    def visit_ClassDef(self, node):
        bases = ", ".join(getattr(b, "id", getattr(b, "attr", "")) for b in node.bases if hasattr(b, "id") or hasattr(b, "attr"))
        self.res["symbols"].append(sym(node.name, "class", node.lineno, node.end_lineno or node.lineno,
                                       f"class {node.name}({bases})", self._doc(node),
                                       parent=".".join(self.class_stack) or None,
                                       exported=1))
        self._route(node, node.name)
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()

    def visit_FunctionDef(self, node):
        kind = "method" if self.class_stack else "function"
        args = [a.arg for a in node.args.args]
        self.res["symbols"].append(sym(node.name, kind, node.lineno, node.end_lineno or node.lineno,
                                       f"def {node.name}({', '.join(args)})"[:120], self._doc(node),
                                       parent=".".join(self.class_stack) or None, exported=not node.name.startswith("_")))
        self._route(node, node.name)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Import(self, node):
        for alias in node.names:
            self.res["refs"].append({"dst_name": alias.name, "kind": "import", "line": node.lineno})

    def visit_ImportFrom(self, node):
        if node.module and node.level == 0:
            for alias in node.names:
                self.res["refs"].append({"dst_name": f"{node.module}.{alias.name}", "kind": "import", "line": node.lineno})


def extract_py(src_bytes: bytes, path: str) -> dict:
    res = new_result(path)
    try:
        tree = pyast.parse(src_bytes.decode("utf8", "replace"))
    except SyntaxError:
        return res
    lines = src_bytes.decode("utf8", "replace").splitlines()
    _PyVisitor(res, lines).visit(tree)

    # call edges: Name calls that match defined/imported top-level names
    defined = {s["name"] for s in res["symbols"]}
    imported = set()
    for r in res["refs"]:
        if r["kind"] == "import":
            imported.add(r["dst_name"].split(".")[-1])
    class CallVisitor(pyast.NodeVisitor):
        def visit_Call(self, node):
            f = node.func
            name = None
            if isinstance(f, pyast.Name):
                name = f.id
            elif isinstance(f, pyast.Attribute):
                name = f.attr
            if name and (name in defined or name in imported):
                res["refs"].append({"dst_name": name, "kind": "call", "line": getattr(node, "lineno", 0)})
            self.generic_visit(node)
    CallVisitor().visit(tree)
    return res


# ---------------------------------------------------------------- Go
def extract_go(src_bytes: bytes, path: str) -> dict:
    res = new_result(path)
    from tree_sitter import Language, Parser
    import tree_sitter_go
    parser = Parser(Language(tree_sitter_go.language()))
    tree = parser.parse(src_bytes)
    src = src_bytes

    for imp in _walk(tree.root_node, {"import_declaration"}):
        for spec in _walk(imp, {"import_spec"}):
            p = spec.child_by_field_name("path")
            if p is not None:
                res["refs"].append({"dst_name": _node_text(p, src).strip('"'), "kind": "import",
                                    "line": spec.start_point[0] + 1})
    for fd in _walk(tree.root_node, {"function_declaration"}):
        nm = fd.child_by_field_name("name")
        if nm is not None:
            res["symbols"].append(sym(_node_text(nm, src), "function", fd.start_point[0] + 1, fd.end_point[0],
                                      _sig_of(fd, src)))
    for md in _walk(tree.root_node, {"method_declaration"}):
        recv = md.child_by_field_name("receiver")
        nm = md.child_by_field_name("name")
        if nm is not None:
            parent = ""
            if recv is not None:
                types = _walk(recv, {"type_identifier"})
                parent = _node_text(types[0], src) if types else ""
            res["symbols"].append(sym(_node_text(nm, src), "method", md.start_point[0] + 1, md.end_point[0],
                                      _sig_of(md, src), parent=parent))
    for td in _walk(tree.root_node, {"type_declaration"}):
        for spec in _walk(td, {"type_spec"}):
            nm = spec.child_by_field_name("name")
            tv = spec.child_by_field_name("type")
            if nm is not None and tv is not None:
                kind = {"struct_type": "struct", "interface_type": "interface"}.get(tv.type, "type")
                res["symbols"].append(sym(_node_text(nm, src), kind, spec.start_point[0] + 1, spec.end_point[0]))
    for call in _walk(tree.root_node, {"call_expression"}):
        fn = call.child_by_field_name("function")
        args = call.child_by_field_name("arguments")
        if fn is None or args is None or not args.named_children:
            continue
        fname = _node_text(fn, src)
        res["refs"].append({"dst_name": fname, "kind": "call", "line": call.start_point[0] + 1})
        parts = fname.split(".")
        if len(parts) >= 2 and parts[-1].lower() in HTTP_METHODS:
            a0 = args.named_children[0]
            if a0 and a0.type == "raw_string_literal":
                route = _node_text(a0, src).strip('`"')
                res["routes"].append({"method": parts[-1].upper(), "route": route, "handler_symbol": None, "auth": None})
    return res


# ---------------------------------------------------------------- SQL / Prisma
_SQL_TABLE = re.compile(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\w\"'`\[\].]*?[\.\"'`\]]?(\w+)\"?\s*\(", re.I)
_SQL_VIEW = re.compile(r"CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(\w+)", re.I)
_SQL_TYPE = re.compile(r"CREATE\s+TYPE\s+(\w+)", re.I)
_SQL_FN = re.compile(r"CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+(\w+)", re.I)
_SQL_POLICY = re.compile(r"CREATE\s+POLICY\s+[\"']?([\w\- ]+)[\"']?\s+ON\s+(\w+)", re.I)
_PRISMA_MODEL = re.compile(r"^model\s+(\w+)\s*\{", re.M)


def extract_sql(src_bytes: bytes, path: str) -> dict:
    res = new_result(path)
    text = src_bytes.decode("utf8", "replace")
    seen = set()
    for pat, kind in [(_SQL_TABLE, "table"), (_SQL_VIEW, "view"), (_SQL_TYPE, "type"), (_SQL_FN, "function")]:
        for m in pat.finditer(text):
            name = m.group(1)
            if name.lower() not in seen:
                seen.add(name.lower())
                res["tables"].append({"name": name, "kind": kind})
                line = text[:m.start()].count("\n") + 1
                res["symbols"].append(sym(name, f"sql_{kind}", line, line, exported=1))
    for m in _SQL_POLICY.finditer(text):
        res["symbols"].append(sym(f"RLS:{m.group(2)}.{m.group(1)}", "rls_policy",
                                 text[:m.start()].count("\n") + 1, 0, exported=1))
    return res


def extract_prisma(src_bytes: bytes, path: str) -> dict:
    res = new_result(path)
    text = src_bytes.decode("utf8", "replace")
    for m in _PRISMA_MODEL.finditer(text):
        res["tables"].append({"name": m.group(1), "kind": "table"})
        res["symbols"].append(sym(m.group(1), "prisma_model", text[:m.start()].count("\n") + 1, 0, exported=1))
    return res


def extract(src_bytes: bytes, lang: str, path: str) -> dict:
    if lang in ("ts", "tsx", "js", "jsx"):
        try:
            return extract_ts(src_bytes, lang, path)
        except Exception:
            return new_result(path)
    if lang == "py":
        return extract_py(src_bytes, path)
    if lang == "go":
        return extract_go(src_bytes, path)
    if lang == "sql":
        return extract_sql(src_bytes, path)
    if lang == "prisma":
        return extract_prisma(src_bytes, path)
    return new_result(path)
