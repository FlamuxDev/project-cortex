"""Context packets: task -> budgeted, ranked context for coding agents."""
from __future__ import annotations
import math, re, sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from cortex import search
from cortex.search import keywords, pathlib_stem
from cortex.db import code_root
from cortex.session import live_git

CHARS_PER_TOKEN = 4

SECTION_PRIORITY = [
    "HEADER", "TASK INTERPRETATION", "LIKELY MODULE", "MODULE", "START HERE",
    "PRIMARY FILES", "PRIMARY SYMBOLS", "READ FIRST",
    "IMPORTANT DEPENDENCIES", "DEPENDENCIES", "CALLERS / IMPORTERS",
    "LIKELY IMPACT", "RULES / INVARIANTS", "BUSINESS RULES",
    "API SURFACE HERE", "DATABASE ENTITIES", "TESTS TO RUN", "RELATED TESTS",
    "PAST TASK LESSONS", "HISTORICAL WARNINGS",
    "RECENT RELEVANT CHANGES", "KNOWLEDGE", "SECONDARY FILES IF NEEDED",
]


def _fmt_commit(c):
    return f"{c['sha']} {c['date']} [{c['category']}] {c['subject']}"


def _dedupe(items, key):
    seen, out = set(), []
    for x in items:
        k = key(x)
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out


def build_sections(con, pid: str, task: str,
                   index_sync: dict | None = None) -> list[tuple[str, str]]:
    """Gather all evidence sections for a task in one project."""
    secs: list[tuple[str, str]] = []
    proj = con.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    if proj is None:
        known = [r["id"] for r in con.execute("SELECT id FROM projects ORDER BY id")]
        raise ValueError(f"unknown project {pid!r} — indexed projects: {', '.join(known) or '(none)'}")
    # LIVE freshness — stored head goes stale the moment someone commits
    root = code_root(proj)
    indexed = (proj["indexed_commit"] or "")[:12]
    gitinfo = live_git(root, indexed)
    head, dirty, behind = gitinfo["head"], gitinfo["dirty"], gitinfo["behind"]
    sync_status = (index_sync or {}).get("status")
    if sync_status in {"current", "refreshed"} and head:
        action = "auto-refreshed" if sync_status == "refreshed" else "verified current"
        fresh = (f"⚠ DIRTY — current working-tree snapshot ({action})" if dirty
                 else f"fresh ({action})")
    elif sync_status == "unstable":
        fresh = "⚠ WORKTREE CHANGED DURING INDEX — verify edited files before acting"
    elif sync_status == "failed":
        fresh = ("⚠ AUTO-REFRESH FAILED — " +
                 (index_sync or {}).get("error", "verify against current code"))
    elif not head:
        fresh = ("not available (non-git project)" if not indexed else
                 "⚠ STALE — repository has no readable git HEAD")
    elif head != indexed:
        distance = f"{behind} commit(s)" if behind is not None else "an unknown number of commits"
        fresh = f"brain behind repo by {distance} — run cortex update; verify against current code"
    elif dirty:
        fresh = (f"⚠ DIRTY — {dirty} uncommitted change(s) may differ from the index; "
                 "run cortex update or verify current code")
    else:
        fresh = "fresh"
    # A missing git HEAD makes `behind` 0, which would report a vanished repo as
    # "fresh". Confirm the indexed code is actually on disk before claiming that.
    disk_warning = None
    rootp = pathlib.Path(root)
    if not rootp.is_dir():
        disk_warning = f"project directory {root} DOES NOT EXIST — every path below is stale"
    else:
        sample = [r["path"] for r in con.execute(
            "SELECT path FROM files WHERE project_id=? ORDER BY importance DESC LIMIT 20", (pid,))]
        alive = sum(1 for s in sample if (rootp / s).exists())
        if sample and alive == 0:
            disk_warning = (f"NONE of this project's indexed files exist under {root} — "
                            "the code moved or was deleted; do not trust the paths below")
        elif sample and alive < len(sample) // 2:
            disk_warning = (f"only {alive}/{len(sample)} sampled files still exist under {root} — "
                            "run cortex update and verify before acting")
    if disk_warning:
        fresh = f"⚠ STALE — {disk_warning}"
    langs = ",".join(l.lstrip(".") for l in (proj["languages"] or "").split(",") if l) or "unknown"
    stack = langs + (f" | frameworks: {proj['frameworks']}" if proj["frameworks"] else "")
    header = (f"PROJECT: {proj['name']} ({pid})\nPATH: {root}\nSTACK: {stack}"
              f"\nINDEX SYNC: {sync_status or 'not-checked'}\nFRESHNESS: {fresh}")
    if dirty:
        note = ("indexable code changes are included in this snapshot"
                if sync_status in {"current", "refreshed"}
                else "indexable code may differ from the index")
        header += f"\nNOTE: {dirty} uncommitted change(s) exist; {note}"
    secs.append(("HEADER", header))

    # lexical candidates
    syms_raw = search.search_symbols(con, pid, task, limit=24)
    kws = set(keywords(task))

    # --- unified scoring: keyword-overlap (IDF) >> normalized bm25 > importance
    cand: dict[str, dict] = {}   # path -> {"rank": best positive bm25 quality, "imp": ...}
    def add_cand(path, q, imp):
        e = cand.setdefault(path, {"q": 0.0, "imp": 0.0})
        e["q"] += max(q, 0)
        e["imp"] = max(e["imp"], imp or 0)
    for s in syms_raw:
        add_cand(s["path"], -s["rank"], s["importance"])
    for r in search.search_files(con, pid, task, limit=12):
        add_cand(r["path"], -r["rank"], r["importance"])
    max_q = max((e["q"] for e in cand.values()), default=1.0) or 1.0

    # semantic anchor: paths/prefixes cited by task-matching memories get the
    # strongest boost (module memories cite path_prefixes, incl. {a,b} braces)
    mem_prefixes: list[str] = []
    import json as _json
    for m in search.search_memories(con, pid, task, limit=6):
        try:
            for s in _json.loads(m.get("source_files_json") or "[]"):
                mem_prefixes.append(s.strip())
        except Exception:
            pass
        mm = re.search(r"path_prefixes\s*:\s*(.+)", m["body_md"])
        if mm:
            for part in mm.group(1).split(","):
                part = part.strip().strip("`")
                mem_prefixes.append(part)
        for token in re.findall(r"[\w./\-]+\.\w{1,4}", m["body_md"]):
            if "/" in token:
                mem_prefixes.append(token)

    def expand_braces(prefix: str) -> list[str]:
        import re as _re
        m = _re.search(r"\{([^}]+)\}", prefix)
        if not m:
            return [prefix]
        out = []
        for alt in m.group(1).split(","):
            out.extend(expand_braces(prefix[:m.start()] + alt.strip() + prefix[m.end():]))
        return out

    expanded = []
    for mp in mem_prefixes:
        if len(mp) < 5:
            continue
        expanded.extend(expand_braces(mp))

    def mem_boost(path: str) -> float:
        best = 0.0
        for mp in expanded:
            if path == mp or path.endswith(mp) or ("/" + mp + "/") in "/" + path or path.startswith(mp):
                best = max(best, 8.0)
            elif mp.lstrip("./") in path:
                best = max(best, 4.0)
        return best
    paths = [(r["path"], r["importance"]) for r in
             con.execute("SELECT path, importance FROM files WHERE project_id=?", (pid,))]
    strong_kws = {k for k in kws if len(k) > 3}
    df = {k: sum(1 for p, _ in paths if k in p.lower()) for k in strong_kws}
    n_docs = max(len(paths), 1)

    def kw_score(path: str) -> float:
        pl = path.lower()
        return sum(math.log(n_docs / max(df[k], 1)) + 0.5 for k in strong_kws if k in pl)

    file_scores = {}
    for p, e in cand.items():
        file_scores[p] = (10.0 * kw_score(p) / 7.0 + 4.0 * (e["q"] / max_q)
                          + 0.02 * e["imp"] + mem_boost(p))
    # guarantee sweep over ALL project paths (FTS pool may miss named targets)
    for p, imp in paths:
        ks = kw_score(p)
        if ks:
            file_scores[p] = file_scores.get(p, 0) + 10.0 * ks / 7.0 + 0.02 * imp
    for p in list(file_scores):
        b = mem_boost(p)
        if b:
            file_scores[p] += b
    file_scores = {p: sc for p, sc in file_scores.items()}
    syms = sorted(syms_raw, key=lambda s: -(kw_score(s["path"]) * 1.5 + max(-s["rank"], 0.01) + s["importance"] * 0.05))
    # module-memory paths boost matching files
    mems = search.search_memories(con, pid, task, limit=12)
    kb_lines = []
    rule_lines = []
    warn_lines = []
    for m in mems:
        stale_mark = " [STALE]" if m["stale"] else ""
        entry = f"- [{m['scope']}|{m['confidence']}]{stale_mark} {m['title']}: " + \
                m["body_md"][:500].replace("\n", " ")
        if m["scope"] == "pitfall":
            warn_lines.append(entry)
        elif m["scope"] in ("module", "project", "architecture"):
            kb_lines.append(entry)
        else:
            rule_lines.append(entry)

    ranked = sorted(file_scores.items(), key=lambda kv: -kv[1])[:10]
    # existence guardrail: surface task terms absent from the whole project
    corpus = " \n ".join(p for p, _ in paths).lower()
    best_sym_q = max((max(-s["rank"], 0) for s in syms_raw), default=0)
    if best_sym_q > 0:
        try:
            corpus += " \n " + " ".join(s["name"].lower() for s in syms_raw)
        except Exception:
            pass
    missing = sorted(k for k in strong_kws if k not in corpus)
    multi = sum(1 for p, _ in ranked[:3]
                if sum(1 for k in strong_kws if k in p.lower()) >= 2)
    if missing and multi == 0:
        secs.append(("⚠ EVIDENCE WARNING",
                     f"These task terms appear NOWHERE in this project's indexed paths/symbols: "
                     f"{', '.join(missing)}. The feature may not exist here or uses other "
                     f"terminology. Matches below share only partial terms ({', '.join(sorted(strong_kws - set(missing))) or 'none'}) — "
                     f"verify before acting."))
    if ranked:
        secs.append(("PRIMARY FILES", "\n".join(f"{p}" for p, _ in ranked)))
        mod = search.module_for_path(con, pid, ranked[0][0])
        if mod:
            secs.append(("MODULE", f"{mod['name']} [{mod['confidence']}]\npurpose: {mod['purpose']}\nowns: {mod['path_prefixes']}"))
        sym_lines = []
        for s in syms[:8]:
            sig = (s["signature"] or "").replace("\n", " ")[:110]
            sym_lines.append(f"{s['path']}:{s['line_start']} {s['kind']} {s['name']}  {sig}")
        if sym_lines:
            secs.append(("PRIMARY SYMBOLS", "\n".join(sym_lines)))
        secs.append(("READ FIRST", "\n".join(p for p, _ in ranked[:6])))

        callers, tests, apis, dbents = {}, [], [], []
        for p, _ in ranked[:5]:
            cl = search.callers_of(con, pid, p)
            if cl:
                callers[p] = cl[:8]
            tests += search.tests_for_paths(con, pid, [p], limit=4)
            apis += search.apis_for_path(con, pid, p, limit=4)
            dbents += search.db_entities_for_file(con, pid, p)
        tests = _dedupe(tests, lambda t: t["path"])[:8]
        apis = _dedupe(apis, lambda a: f"{a['method']}{a['route']}")[:8]
        dbents = _dedupe(dbents, lambda d: d["name"])[:10]

        if callers:
            secs.append(("CALLERS / IMPORTERS", "\n".join(
                f"{p}\n  <- " + ", ".join(cl) for p, cl in callers.items())))
        impact_files = sorted({c for cl in callers.values() for c in cl})
        risk = "high" if len(impact_files) > 6 or apis else ("medium" if impact_files else "low")
        why = []
        if len(impact_files) > 6:
            why.append(f"{len(impact_files)} dependent files")
        if apis:
            why.append(f"{len(apis)} API route(s) served here")
        if any(t["direct"] for t in tests):
            why.append("tests directly cover these files")
        if dbents:
            why.append(f"{len(dbents)} DB entities referenced")
        secs.append(("LIKELY IMPACT",
                     f"risk={risk} ({'; '.join(why) or 'isolated'})" +
                     ("\nindirectly touched:\n" + "\n".join(impact_files[:10]) if impact_files else "")))
        if tests:
            secs.append(("TESTS TO RUN", "\n".join(
                f"{t['path']} ({t['kind']}{' DIRECT' if t['direct'] else ''})" for t in tests)))
        if apis:
            secs.append(("API SURFACE HERE", "\n".join(
                f"{a['method']} {a['route']} -> {(a['handler_symbol'] or '?')[:50]}" for a in apis)))
        if dbents:
            secs.append(("DATABASE ENTITIES", "\n".join(
                f"{d['kind']} {d['name']} defined in {d['file_path']}" for d in dbents)))

        hist = search.recent_commits(con, pid, paths=[p for p, _ in ranked[:4]], limit=6)
        if hist:
            secs.append(("RECENT RELEVANT CHANGES", "\n".join(_fmt_commit(c) for c in hist)))
        warns = [c for c in search.recent_commits(con, pid, paths=[p for p, _ in ranked[:3]], limit=40)
                 if c["category"] in ("fix",)]
        if warns:
            secs.append(("HISTORICAL WARNINGS", "\n".join(
                f"past fix here: {_fmt_commit(c)}" for c in warns[:5])))
        dep_lines = []
        for p, _ in ranked[:3]:
            imps = [dp or dn for dp, dn in search.imports_of(con, pid, p, limit=14)]
            if imps:
                dep_lines.append(f"{p}\n  imports: " + ", ".join(imps))
        if dep_lines:
            secs.append(("DEPENDENCIES", "\n".join(dep_lines)))

    if rule_lines:
        secs.append(("RULES / INVARIANTS", "\n".join(rule_lines[:6])))
        secs.append(("BUSINESS RULES", "\n".join(rule_lines[:6])))
    if warn_lines:
        secs.append(("KNOWN PITFALLS", "\n".join(warn_lines[:6])))
    if kb_lines:
        secs.append(("KNOWLEDGE", "\n".join(kb_lines[:6])))

    # closed learning loop: relevant episodes from completed tasks
    try:
        from cortex.session import relevant_episodes
        eps = relevant_episodes(con, pid, task)
        ep_lines = []
        for ep in eps:
            tag = f"[{ep['outcome'] or 'done'}"
            if ep["outcome"] == "failed":
                tag += " ATTEMPT — do not repeat"
            tag += f" | {ep['confidence']}]"
            body = (ep["lessons"] or ep["solution"] or "")[:400]
            ep_lines.append(f"- {tag} {ep['task'][:90]}\n  {body}")
        if ep_lines:
            secs.append(("PAST TASK LESSONS",
                         "validated knowledge from previous tasks in this project:\n"
                         + "\n".join(ep_lines)))
    except Exception:
        pass

    secs.append(("TASK INTERPRETATION", "focus terms: " + ", ".join(keywords(task)[:10])))
    return secs


CROSS_CUES = ("across projects", "all projects", "every project", "which projects",
              "elsewhere", "other projects", "in the past", "have we ", "did we ",
              "قبل", "سابقا")


def context_cross(con, task: str, budget: int = 4000,
                  refresh: str = "auto") -> dict:
    """Cross-project query: group matching memories/symbols by project."""
    from cortex.indexer import refresh_project
    sync = {}
    for row in con.execute("SELECT id FROM projects WHERE status='active' ORDER BY id"):
        sync[row["id"]] = refresh_project(con, row["id"], mode=refresh)
    limit_chars = budget * CHARS_PER_TOKEN
    mems = search.search_memories(con, None, task, limit=24)
    syms = search.search_symbols(con, None, task, limit=30)
    files = search.search_files(con, None, task, limit=20)
    if not (mems or syms or files):
        return {"packet": f"NO EVIDENCE for '{task}' in any indexed project.",
                "tokens_est": 12, "truncated": False, "index_sync": sync}
    sync_line = ", ".join(f"{pid}={result.get('status', 'unknown')}"
                          for pid, result in sync.items())
    prefix = f"## INDEX SYNC\n{sync_line or 'no active projects'}\n\n## CROSS-PROJECT RESULTS\n"
    used = len(prefix)
    out = [prefix]
    def emit(pid, line):
        nonlocal used
        block = f"[{pid or '?'}] {line}\n"
        if used + len(block) <= limit_chars:
            out.append(block)
            used += len(block)
            return True
        return False
    seen_titles = set()
    # interleave per-project so one noisy project can't crowd out the rest
    strong_kws_x = {k for k in keywords(task) if len(k) > 3}

    def focus(m):
        text = (m["title"] + " " + m["body_md"][:300]).lower()
        return (-sum(1 for k in strong_kws_x if k in text), m["rank"])

    mem_queues: dict[str, list] = {}
    for m in sorted(mems, key=lambda x: x["rank"]):
        key = (m["project_id"] or "?", m["title"])
        if key in seen_titles:
            continue
        seen_titles.add(key)
        mem_queues.setdefault(m["project_id"] or "global", []).append(m)
    for k in mem_queues:
        mem_queues[k].sort(key=focus)
    order = sorted(mem_queues, key=lambda k: -len(mem_queues[k]))
    emitted_any = True
    while emitted_any:
        emitted_any = False
        for k in order:
            q = mem_queues.get(k) or []
            if not q:
                continue
            m = q.pop(0)
            stale = " [STALE]" if m["stale"] else ""
            if emit(k, f"MEM [{m['scope']}|{m['confidence']}]{stale} {m['title']}: "
                       f"{m['body_md'][:220].replace(chr(10),' ')}"):
                emitted_any = True
    for s in syms[:15]:
        if not emit(s["project_id"], f"SYM {s['path']}:{s['line_start']} [{s['kind']}] {s['name']}"):
            break
    packet = "".join(out).strip()
    projs_touched = sorted({m["project_id"] for m in mems if m["project_id"]} |
                           {s["project_id"] for s in syms})
    return {"packet": packet, "tokens_est": used // CHARS_PER_TOKEN,
            "truncated": used >= limit_chars, "projects": projs_touched,
            "index_sync": sync}


def context(con, task: str, project_id: str | None = None, budget: int = 4000,
            include_global: bool = True, refresh: str = "auto") -> dict:
    tl = task.lower()
    if project_id is None and any(c in tl for c in CROSS_CUES):
        return context_cross(con, task, budget, refresh=refresh)
    explicit_or_cwd_project = project_id
    pid = project_id or search.detect_named_project(con, task)
    if not pid:
        return {"error": "could not determine target project; pass project explicitly"}
    if not explicit_or_cwd_project:
        # lexical-only guess: require the task to match something real in that project
        kws = keywords(task)[:8]
        hit = []
        for k in kws:
            hit = con.execute(
                "SELECT 1 FROM symbols WHERE project_id=? AND (name LIKE ? OR path LIKE ?) LIMIT 1",
                (pid, f"%{k}%", f"%{k}%")).fetchall()
            if hit:
                break
        if not hit and kws:
            hit = con.execute("SELECT 1 FROM files WHERE project_id=? AND path LIKE ? LIMIT 1",
                              (pid, f"%{kws[0]}%")).fetchall()
        if not hit:
            return {"error": (f"task matches no evidence in '{pid}' (lexical guess only); "
                              "pass --project explicitly or run inside the project directory")}
    from cortex.indexer import refresh_project
    index_sync = refresh_project(con, pid, mode=refresh)
    limit_chars = budget * CHARS_PER_TOKEN
    sections = build_sections(con, pid, task, index_sync=index_sync)

    if include_global:
        gmems = search.search_memories(con, None, task, limit=3)
        for g in gmems:
            if g["project_id"] is None:
                sections.append(("GLOBAL KNOWLEDGE",
                                 f"- {g['title']}: {g['body_md'][:300]}"))

    used = 0
    rendered = []
    order = {name: i for i, name in enumerate(SECTION_PRIORITY)}
    for name, text in sorted(sections, key=lambda kv: order.get(kv[0], 90)):
        block = f"\n## {name}\n{text}\n"
        if used + len(block) <= limit_chars:
            rendered.append(block)
            used += len(block)
        else:
            remaining = limit_chars - used
            if remaining > 300:
                rendered.append(block[:remaining])
                used += remaining
            break
    packet = "".join(rendered).strip()
    return {"project": pid, "packet": packet, "tokens_est": used // CHARS_PER_TOKEN,
            "truncated": used >= limit_chars, "index_sync": index_sync}


def impact(con, target: str, project_id: str | None = None) -> dict:
    """Estimate blast radius of changing a file / symbol / feature."""
    pid = project_id or search.detect_project(con, target)
    if not pid:
        return {"error": "unknown project"}
    is_pathish = "/" in target or "." in target.split()[-1]
    direct_paths: set[str] = set()

    if is_pathish:
        rows = con.execute("""SELECT path FROM files WHERE project_id=? AND path LIKE ?
                               ORDER BY importance DESC LIMIT 3""", (pid, f"%{target}%")).fetchall()
        direct_paths |= {r["path"] for r in rows}
    if not direct_paths:
        for s in search.search_symbols(con, pid, target, limit=6):
            direct_paths.add(s["path"])
    if not direct_paths:
        for r in search.search_files(con, pid, target, limit=5):
            direct_paths.add(r["path"])
    if not direct_paths:
        return {"error": f"no file/symbol match for '{target}' in {pid}"}

    callers: set[str] = set()
    for p in direct_paths:
        callers |= set(search.callers_of(con, pid, p))
        callers |= set(search.importers_of(con, pid, p))
        # barrel/re-export fallback: files importing something named like this
        # file's stem (unresolved imports) — may include false positives
        stem = pathlib_stem(p)
        if len(stem) > 4:
            for r in con.execute("""SELECT DISTINCT src_path FROM refs WHERE project_id=?
                                    AND kind='import' AND dst_path IS NULL AND dst_name LIKE ?
                                    LIMIT 10""", (pid, f"%{stem}")):
                if r["src_path"] != p:
                    callers.add(r["src_path"])
    indirect = set()
    frontier = list(callers)
    depth_guard = 0
    while frontier and depth_guard < 12 and len(indirect) < 60:
        p = frontier.pop()
        more = set(search.importers_of(con, pid, p, limit=10)) - callers - direct_paths - indirect
        indirect |= more
        frontier.extend(list(more)[:5])
        depth_guard += 1

    tests = _dedupe(search.tests_for_paths(con, pid, list(direct_paths | callers), limit=20),
                    lambda t: t["path"])
    apis, dbents = [], []
    for p in direct_paths:
        apis += search.apis_for_path(con, pid, p, limit=10)
        dbents += search.db_entities_for_file(con, pid, p)
    apis = _dedupe(apis, lambda a: f"{a['method']}{a['route']}")
    dbents = _dedupe(dbents, lambda d: d["name"])

    risk, reasons = "low", []
    n = len(callers) + len(indirect)
    if apis:
        risk = max_risk(risk, "medium")
        reasons.append(f"serves {len(apis)} API route(s)")
    if dbents:
        risk = max_risk(risk, "medium")
        reasons.append(f"touches DB entities: {', '.join(d['name'] for d in dbents[:5])}")
    if n > 15:
        risk = "high"
        reasons.append(f"{n} dependent files")
    elif n > 5:
        risk = max_risk(risk, "medium")
        reasons.append(f"{n} dependent files")
    if tests:
        risk = max_risk(risk, "low")
        reasons.append(f"{len(tests)} test files reference this area")

    mod = None
    first = sorted(direct_paths)[0]
    mod = search.module_for_path(con, pid, first)
    recent = search.recent_commits(con, pid, paths=list(direct_paths)[:3], limit=5)
    fixes = [c for c in search.recent_commits(con, pid, paths=list(direct_paths)[:3], limit=30)
             if c["category"] == "fix"][:3]

    return {
        "project": pid,
        "targets": sorted(direct_paths),
        "module": mod["name"] if mod else None,
        "risk": risk,
        "reasons": reasons,
        "direct_dependents": sorted(callers),
        "indirect_dependents": sorted(indirect)[:25],
        "tests": [t["path"] for t in tests],
        "apis": [f"{a['method']} {a['route']}" for a in apis],
        "db_entities": [f"{d['kind']} {d['name']}" for d in dbents],
        "recent_commits": [_fmt_commit(c) for c in recent],
        "past_fixes": [_fmt_commit(c) for c in fixes],
        "_hint": "run related tests; check callers before signature changes",
    }


def max_risk(a: str, b: str) -> str:
    order = {"low": 0, "medium": 1, "high": 2}
    return a if order[a] >= order[b] else b


def context_text(con, task: str, project_id=None, budget=4000,
                 refresh: str = "auto") -> str:
    r = context(con, task, project_id, budget, refresh=refresh)
    return r.get("packet") or r.get("error", "")
