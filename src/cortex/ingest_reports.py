"""Ingest delegate REPORT.md files into the knowledge base."""
from __future__ import annotations
import json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from cortex.db import connect
from cortex.indexer import slugify
from cortex.langs import redact

REPORTS_DIR = pathlib.Path(__file__).resolve().parents[2] / "projects"

SECTIONS = ["META", "OVERVIEW", "ARCHITECTURE", "MODULES", "FLOWS", "APIS", "DATABASE",
            "TESTS", "GIT LESSONS", "DECISIONS", "RISKS & TECH DEBT", "UNCERTAIN"]


def parse_report(text: str) -> dict:
    # split into H2 sections
    parts = re.split(r"^## +(.+?)\s*$", text, flags=re.M)
    title = parts[0].strip().lstrip("# ").strip() if parts else ""
    secs: dict[str, str] = {}
    i = 1
    while i < len(parts) - 0:
        name = parts[i].strip().upper()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        secs[name] = body.strip()
        i += 2
    return {"title": title, "sections": secs}


def parse_meta(body: str) -> dict:
    meta = {}
    for line in body.splitlines():
        if ":" in line and not line.startswith("#"):
            k, _, v = line.partition(":")
            meta[k.strip().lower().replace(" ", "_")] = v.strip()
    return meta


def parse_modules(body: str) -> list[dict]:
    mods = []
    blocks = re.split(r"^### +(.+?)\s*$", body, flags=re.M)
    i = 1
    while i < len(blocks) - 1:
        heading, content = blocks[i], blocks[i + 1]
        m = {"heading": heading}
        for key in ["purpose", "path_prefixes", "key_files", "entrypoints", "responsibilities",
                    "invariants", "pitfalls", "confidence"]:
            mm = re.search(rf"^\*?{key}\*?\s*:\s*(.+)$", content, flags=re.M | re.I)
            if mm:
                m[key] = mm.group(1).strip()
        conf = m.get("confidence", "inferred").lower()
        if conf not in ("verified", "strongly_inferred", "inferred", "uncertain"):
            conf = "inferred"
        m["confidence"] = conf
        m["body"] = content.strip()
        mods.append(m)
        i += 2
    return mods


def parse_flows(body: str) -> list[dict]:
    flows = []
    blocks = re.split(r"^### +(.+?)\s*$", body, flags=re.M)
    i = 1
    while i < len(blocks) - 1:
        heading, content = blocks[i], blocks[i + 1]
        f = {"name": heading.split("—")[0].strip(), "body": content.strip()}
        mm = re.search(r"^files\s*:\s*(.+)$", content, flags=re.M | re.I)
        if mm:
            f["files"] = [x.strip() for x in mm.group(1).split(",") if x.strip()]
        fc = re.search(r"^confidence\s*:\s*(\w+)", content, flags=re.M | re.I)
        f["confidence"] = fc.group(1) if fc else "inferred"
        flows.append(f)
        i += 2
    return flows


def ingest_report(con, report_path: pathlib.Path, project_id: str) -> dict:
    parsed = parse_report(report_path.read_text())
    S = parsed["sections"]
    meta = parse_meta(S.get("META", ""))
    counts = {"memories": 0, "modules": 0, "flows": 0, "decisions": 0}

    head_sha = None
    row = con.execute("SELECT git_head FROM projects WHERE id=?", (project_id,)).fetchone()
    if row:
        head_sha = (row["git_head"] or "")[:12]

    def add_memory(scope, title, body_md, confidence, sources=None):
        con.execute("""INSERT INTO memories(project_id,scope,title,body_md,confidence,origin,
                       source_files_json,evidence_json,verified_at_commit)
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    (project_id, scope, redact(title)[:200], redact(body_md), confidence,
                     "delegate", json.dumps(sources or []), None, head_sha))
        counts["memories"] += 1

    if S.get("OVERVIEW"):
        add_memory("project", f"{meta.get('root','').split('/')[-1] or project_id}: overview",
                   S["OVERVIEW"], "verified")
    if S.get("ARCHITECTURE"):
        add_memory("architecture", "Architecture", S["ARCHITECTURE"], "strongly_inferred")
    if S.get("DATABASE"):
        add_memory("architecture", "Database", S["DATABASE"], "strongly_inferred")
    if S.get("TESTS"):
        add_memory("project", "Tests & commands", S["TESTS"], "verified")
    if S.get("APIS"):
        add_memory("architecture", "API surface", S["APIS"], "strongly_inferred")
    if S.get("RISKS & TECH DEBT"):
        add_memory("pitfall", "Risks & technical debt", S["RISKS & TECH DEBT"], "verified")

    for lesson_title, key in [("Historical lessons", "GIT LESSONS")]:
        if S.get(key):
            add_memory("history", lesson_title, S[key], "verified")

    for m in parse_modules(S.get("MODULES", "")):
        name_part = m["heading"].split("—")[-1].strip()
        mslug = slugify(name_part)
        mid = f"{project_id}:{mslug}"
        prefixes = [p.strip() for p in m.get("path_prefixes", "").split(",") if p.strip()]
        con.execute("""INSERT INTO modules(id,project_id,name,slug,path_prefixes,purpose,body_md,
                       confidence,verified_at_commit)
                       VALUES (?,?,?,?,?,?,?,?,?)
                       ON CONFLICT(id) DO UPDATE SET purpose=excluded.purpose,
                         body_md=excluded.body_md, confidence=excluded.confidence,
                         path_prefixes=excluded.path_prefixes,
                         verified_at_commit=excluded.verified_at_commit""",
                    (mid, project_id, name_part[:100], mslug, ",".join(prefixes),
                     m.get("purpose", "")[:300], redact(m["body"]), m["confidence"], head_sha))
        for pf in prefixes:
            for r in con.execute(
                    "SELECT path FROM files WHERE project_id=? AND (path LIKE ? OR path LIKE ?)",
                    (project_id, pf + "%", "%/" + pf + "%")):
                con.execute("INSERT OR IGNORE INTO module_files(module_id,project_id,path) VALUES (?,?,?)",
                            (mid, project_id, r["path"]))
        counts["modules"] += 1
        add_memory("module", f"Module: {name_part}", m["body"], m["confidence"],
                   sources=m.get("key_files", "").split(", ") if m.get("key_files") else [])

    for f in parse_flows(S.get("FLOWS", "")):
        fid = f"{project_id}:{slugify(f['name'])}"
        trigger = re.search(r"^trigger\s*:\s*(.+)$", f["body"], flags=re.M | re.I)
        con.execute("""INSERT INTO flows(id,project_id,name,trigger,steps_md,files_json,confidence)
                       VALUES (?,?,?,?,?,?,?)
                       ON CONFLICT(id) DO UPDATE SET steps_md=excluded.steps_md,
                         files_json=excluded.files_json, confidence=excluded.confidence""",
                    (fid, project_id, f["name"][:150],
                     trigger.group(1)[:300] if trigger else "", f["body"],
                     json.dumps(f.get("files", [])), f["confidence"]))
        counts["flows"] += 1

    dec_body = S.get("DECISIONS", "")
    if dec_body:
        # each line/bullet starting with '-' or '###' becomes a decision
        entries = re.split(r"\n(?=(?:[-*]|#{3,}) )", dec_body)
        for e in entries:
            e = e.strip()
            if not e or len(e) < 15:
                continue
            title = e.lstrip("-*# ").split("\n")[0][:150]
            sha = re.search(r"\b([0-9a-f]{7,12})\b", e)
            con.execute("""INSERT INTO decisions(project_id,title,context,decision,date,commit_sha,
                           source,confidence) VALUES (?,?,?,?,?,?,?,?)""",
                        (project_id, redact(title), e[:2000], "", "",
                         sha.group(1) if sha else None, report_path.name, "delegate_reported"))
            counts["decisions"] += 1

    unc = S.get("UNCERTAIN", "")
    if unc:
        con.execute("""INSERT INTO memories(project_id,scope,title,body_md,confidence,origin,
                       verified_at_commit) VALUES (?,?,?,?,?,?,?)""",
                    (project_id, "uncertain", "Open questions / unverified claims",
                     redact(unc), "uncertain", "delegate", head_sha))
        counts["memories"] += 1
    return counts


def ingest_all(con) -> dict:
    results = {}
    for d in sorted(REPORTS_DIR.iterdir()):
        rp = d / "REPORT.md"
        if not rp.exists():
            continue
        pid = d.name
        if not con.execute("SELECT 1 FROM projects WHERE id=?", (pid,)).fetchone():
            results[pid] = "SKIPPED (project not indexed)"
            continue
        con.execute("DELETE FROM memories WHERE project_id=? AND origin='delegate'", (pid,))
        con.execute("DELETE FROM module_files WHERE module_id IN (SELECT id FROM modules WHERE project_id=?)", (pid,))
        con.execute("DELETE FROM modules WHERE project_id=?", (pid,))
        con.execute("DELETE FROM flows WHERE project_id=?", (pid,))
        con.execute("DELETE FROM decisions WHERE project_id=? AND source LIKE 'REPORT%'", (pid,))
        results[pid] = ingest_report(con, rp, pid)
    from cortex.indexer import _refresh_memory_fts
    _refresh_memory_fts(con)
    con.commit()
    return results


if __name__ == "__main__":
    con = connect()
    res = ingest_all(con)
    for pid, r in res.items():
        print(pid, r)
