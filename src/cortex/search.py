"""Hybrid retrieval: lexical (FTS5 BM25) + graph signals + importance."""
from __future__ import annotations
import json, pathlib, re

STOP = set("""a an the is are was were be been to of in on for with and or not this that these those
how what when where which who why does do did can could should would will i we you it its as at by
from into if then else there here my our your their me us them""".split())

AR_STOP = {"في","من","على","عن","الى","إلى","هذا","هذه","التي","الذي","ما","هل","كيف","أين","اين","مع","عند","عدل"}

# AR->EN glossary so Arabic tasks hit English code/memories. The shipped table is
# a generic starter; extend it per install via $CORTEX_HOME/glossary.json
# ({"terms": {"<arabic>": ["<english>", ...]}}) — user entries override and extend.
def _load_glossary() -> dict[str, list[str]]:
    terms: dict[str, list[str]] = {}
    shipped = pathlib.Path(__file__).parent / "data" / "glossary_ar.json"
    from cortex.db import cortex_home
    for src in (shipped, cortex_home() / "glossary.json"):
        try:
            data = json.loads(src.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # missing or malformed: never let a bad glossary break search
        for k, v in (data.get("terms") or {}).items():
            if isinstance(v, list):
                terms[k] = [str(x) for x in v]
    return terms


AR_EN = _load_glossary()


AR_PUNCT = "؟?،؛:.!«»()[]{}\"'\u061f\u06cc"


def keywords(q: str) -> list[str]:
    words = re.findall(r"[\w\u0600-\u06FF]+", q.lower())
    words = [w.strip(AR_PUNCT) for w in words]
    words = [w for w in words if w]
    out = [w for w in words if w not in STOP and w not in AR_STOP and len(w) > 1]
    extra = []
    for w in out:
        extra.extend(AR_EN.get(w, []))
        # strip definite article ال for lookup
        base = w[2:] if w.startswith("ال") else w
        extra.extend(AR_EN.get(base, []))
        # naive plural ة→at / at→ة bridging for common nouns
        if base.endswith("ات") and base[:-2] in AR_EN:
            extra.extend(AR_EN[base[:-2]])
    # dedup: the article-stripping and plural paths re-hit the same glossary
    # entry, and duplicates would burn slots in fts_query's 12-term cap
    seen = set(out)
    return out + [e for e in extra
                  if e not in STOP and not (e in seen or seen.add(e))]


def fts_query(q: str) -> str:
    """OR-combine terms for recall; BM25 + downstream rerank handle precision."""
    return " OR ".join(f'"{w}"*' for w in keywords(q)[:12])


def search_symbols(con, project_id: str | None, q: str, limit=15):
    qq = fts_query(q)
    if not qq:
        return []
    sql = """SELECT f.rowid AS rid, s.id, s.project_id, s.path, s.name, s.kind, s.line_start,
                    s.signature, s.importance, bm25(fts_symbols, 3.0, 2.0, 1.0, 0.5) AS rank
             FROM fts_symbols f JOIN symbols s ON s.rowid=f.rowid
             WHERE fts_symbols MATCH ?"""
    args = [qq]
    if project_id:
        sql += " AND s.project_id=?"
        args.append(project_id)
    sql += " ORDER BY rank LIMIT ?"
    args.append(limit * 4)
    rows = [dict(r) for r in con.execute(sql, args)]
    # bm25 rank is negative (lower=better); combine with importance safely in python
    rows.sort(key=lambda r: -((-r["rank"]) + r["importance"] * 0.03))
    return rows[:limit]


def search_memories(con, project_id: str | None, q: str, limit=8, include_global=True):
    qq = fts_query(q)
    if not qq:
        return []
    sql = """SELECT m.rowid AS rid, m.id, m.project_id, m.scope, m.title, m.body_md, m.confidence,
                    m.stale, bm25(fts_memories) AS rank
             FROM fts_memories f JOIN memories m ON m.rowid=f.rowid
             WHERE fts_memories MATCH ?"""
    args = [qq]
    if project_id:
        sql += " AND (m.project_id IS NULL OR m.project_id=?)"
        args.append(project_id)
    rows = con.execute(sql + " ORDER BY rank LIMIT ?", [*args, limit]).fetchall()
    return [dict(r) for r in rows]


def search_files(con, project_id: str | None, q: str, limit=10):
    qq = fts_query(q)
    if not qq:
        return []
    sql = """SELECT ff.rowid AS rid, fl.project_id, fl.path, fl.importance, bm25(fts_files) AS rank
             FROM fts_files ff JOIN files fl ON fl.rowid=ff.rowid
             WHERE fts_files MATCH ?"""
    args = [qq]
    if project_id:
        sql += " AND fl.project_id=?"
        args.append(project_id)
    sql += " ORDER BY rank LIMIT ?"
    args.append(limit * 4)
    rows = [dict(r) for r in con.execute(sql, args)]
    rows.sort(key=lambda r: -((-r["rank"]) + r["importance"] * 0.02))
    return rows[:limit]


def callers_of(con, project_id: str, path: str, symbol: str | None = None, limit=20):
    if symbol:
        rows = con.execute("""SELECT DISTINCT src_path FROM refs WHERE project_id=? AND kind='call'
                              AND dst_name LIKE ? AND (dst_path IS NULL OR dst_path != ?) LIMIT ?""",
                           (project_id, f"%{symbol}", path, limit)).fetchall()
    else:
        rows = con.execute("""SELECT DISTINCT r.src_path FROM refs r WHERE r.project_id=? AND r.dst_path=? 
                              AND r.src_path != ? LIMIT ?""",
                           (project_id, path, path, limit)).fetchall()
    return [r["src_path"] for r in rows]


def importers_of(con, project_id: str, path: str, limit=30):
    rows = con.execute("""SELECT DISTINCT src_path FROM refs WHERE project_id=? AND kind='import'
                          AND dst_path=? AND src_path != ? LIMIT ?""",
                       (project_id, path, path, limit)).fetchall()
    return [r["src_path"] for r in rows]


def imports_of(con, project_id: str, path: str, limit=40):
    rows = con.execute("""SELECT dst_path, dst_name FROM refs WHERE project_id=? AND src_path=?
                          AND kind='import' LIMIT ?""", (project_id, path, limit)).fetchall()
    return [(r["dst_path"], r["dst_name"]) for r in rows]


def module_for_path(con, project_id: str, path: str):
    """Longest path-prefix match wins."""
    best, blen = None, 0
    for m in con.execute("SELECT * FROM modules WHERE project_id=?", (project_id,)).fetchall():
        for pf in (m["path_prefixes"] or "").split(","):
            pf = pf.strip().strip("/")
            if pf and (path == pf or path.startswith(pf + "/") or ("/" + pf + "/") in ("//" + path)):
                if len(pf) > blen:
                    best, blen = m, len(pf)
    return best


def tests_for_paths(con, project_id: str, paths: list[str], limit=15):
    pset = set(paths)
    hits = []
    for t in con.execute("SELECT path,name,kind,targets_json FROM tests WHERE project_id=?", (project_id,)):
        targets = set(json.loads(t["targets_json"] or "[]"))
        stem = t["path"]
        direct = bool(targets & pset)
        name_hit = any(
            pathlib_stem(p) in stem or pathlib_stem(stem).replace(".test", "").replace(".spec", "") in p
            for p in paths)
        if not (direct or name_hit):
            continue
        # same directory/package as the changed code beats distant lookalikes
        samedir = any("/" in t["path"] and t["path"].rsplit("/", 1)[0] == p.rsplit("/", 1)[0]
                      for p in paths)
        hits.append({"path": t["path"], "name": t["name"], "kind": t["kind"],
                     "direct": direct, "_samedir": samedir})
    hits.sort(key=lambda h: (not (h["_samedir"] and h.get("direct")), not h["direct"],
                             not h["_samedir"]))
    out = [{k: v for k, v in h.items() if k != "_samedir"} for h in hits[:limit]]
    return out


def pathlib_stem(p: str) -> str:
    base = p.rsplit("/", 1)[-1]
    return re.sub(r"\.(test|spec)?\.?\w*$", "", base)


def db_entities_for_file(con, project_id: str, path: str):
    return [dict(r) for r in con.execute(
        "SELECT name,kind,file_path FROM db_entities WHERE project_id=? AND file_path=?", (project_id, path))]


def apis_for_path(con, project_id: str, path: str, limit=10):
    return [dict(r) for r in con.execute(
        "SELECT method,route,handler_symbol FROM apis WHERE project_id=? AND handler_path=? LIMIT ?",
        (project_id, path, limit))]


def recent_commits(con, project_id: str, paths: list[str] | None = None, limit=8, category=None):
    if paths:
        marks = ",".join("?" for _ in paths[:20])
        rows = con.execute(f"""SELECT DISTINCT c.sha,c.date,c.subject,c.category FROM commits c
                               JOIN commit_files cf ON cf.project_id=c.project_id AND cf.sha=c.sha
                               WHERE c.project_id=? AND cf.path IN ({marks})
                               ORDER BY c.date DESC LIMIT ?""",
                          (project_id, *paths[:20], limit)).fetchall()
    elif category:
        rows = con.execute("""SELECT sha,date,subject,category FROM commits WHERE project_id=?
                              AND category=? ORDER BY date DESC LIMIT ?""",
                           (project_id, category, limit)).fetchall()
    else:
        rows = con.execute("""SELECT sha,date,subject,category FROM commits WHERE project_id=?
                              ORDER BY date DESC LIMIT ?""", (project_id, limit)).fetchall()
    return [dict(r) for r in rows]


def detect_named_project(con, text: str) -> str | None:
    """Resolve a project only when its id/name is explicitly present in text.

    This is intentionally stricter than lexical evidence ranking: generic task
    words must never route a session to an unrelated repository.
    """
    normalized = re.sub(r"[^\w]+", " ", text.lower()).strip()
    matches: list[tuple[int, str]] = []
    for p in con.execute("SELECT id,name FROM projects"):
        aliases = {p["id"], p["name"] or ""}
        for alias in aliases:
            phrase = re.sub(r"[^\w]+", " ", alias.lower()).strip()
            if len(phrase) < 3:
                continue
            if re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", normalized):
                matches.append((len(phrase), p["id"]))
                break
    if not matches:
        return None
    matches.sort(reverse=True)
    best_len = matches[0][0]
    best = {pid for size, pid in matches if size == best_len}
    return next(iter(best)) if len(best) == 1 else None


def detect_project(con, task: str) -> str | None:
    """Guess target project from a natural-language task."""
    named = detect_named_project(con, task)
    if named:
        return named
    # fall back: which project's evidence matches the task lexically strongest?
    counts: dict[str, int] = {}
    for r in search_files(con, None, task, limit=6):
        counts[r["project_id"]] = counts.get(r["project_id"], 0) + 1
    for r in search_symbols(con, None, task, limit=8):
        counts[r["project_id"]] = counts.get(r["project_id"], 0) + 2
    for r in search_memories(con, None, task, limit=6):
        if r["project_id"]:
            counts[r["project_id"]] = counts.get(r["project_id"], 0) + 3
    return max(counts, key=counts.get) if counts else None
