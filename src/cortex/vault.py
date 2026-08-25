"""Generate the Obsidian vault from the cortex DB.

Generated files carry frontmatter `cortex-generated: true`; anything else is
treated as human-curated and never overwritten.
"""
from __future__ import annotations
import json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from cortex.db import connect

VAULT = pathlib.Path(__file__).resolve().parents[2] / "vault"


def fm(title, tags, extra=""):
    return f"---\ncortex-generated: true\ntitle: {title}\ntags: {tags}\n{extra}---\n"


def is_generated(p: pathlib.Path) -> bool:
    try:
        head = p.read_text()[:200]
        return "cortex-generated: true" in head
    except OSError:
        return True


def w(path: pathlib.Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not is_generated(path):
        return  # never clobber human notes
    path.write_text(content)


def project_status(con, pid):
    p = con.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    def c(sql):
        return con.execute(sql, (pid,)).fetchone()[0]
    behind = 0
    if p["git_head"] and p["indexed_commit"] and p["git_head"][:12] != p["indexed_commit"][:12]:
        row = con.execute("""SELECT COUNT(*) x FROM commits WHERE project_id=? AND date >= COALESCE(
            (SELECT date FROM commits WHERE project_id=? AND sha LIKE ?),'1970-01-01')""",
            (pid, pid, p["indexed_commit"][:12] + "%")).fetchone()
        behind = max(row["x"] - 1, 0)
    return p, {
        "files": c("SELECT COUNT(*) FROM files WHERE project_id=?"),
        "symbols": c("SELECT COUNT(*) FROM symbols WHERE project_id=?"),
        "modules": c("SELECT COUNT(*) FROM modules WHERE project_id=?"),
        "flows": c("SELECT COUNT(*) FROM flows WHERE project_id=?"),
        "apis": c("SELECT COUNT(*) FROM apis WHERE project_id=?"),
        "db": c("SELECT COUNT(*) FROM db_entities WHERE project_id=?"),
        "tests": c("SELECT COUNT(*) FROM tests WHERE project_id=?"),
        "decisions": c("SELECT COUNT(*) FROM decisions WHERE project_id=?"),
        "memories": c("SELECT COUNT(*) FROM memories WHERE project_id=?"),
        "stale_mem": c("SELECT COUNT(*) FROM memories WHERE project_id=? AND stale=1"),
        "behind": behind,
    }


def _deep_pages(con, pid: str, prow) -> int:
    """Six examiner pages per project, all derived from the indexed DB.
    Every fact links back to a real file path."""
    count = 0
    P = VAULT / "Projects" / pid

    # ---------- API SURFACE ----------
    apis = con.execute("""SELECT method, route, handler_path, handler_symbol, direction
                          FROM apis WHERE project_id=? ORDER BY handler_path, route""", (pid,)).fetchall()
    import re as _re
    apis = [a for a in apis if a["handler_path"] and not _re.search(
        r"(^|/)__(tests|e2e)__|\.(test|spec)\.|_test\.", a["handler_path"])]
    body = [fm(f"{pid} api", "[api/project]"),
            f"# {prow['name']} — API Surface", "",
            f"{len(apis)} routes. Grouped by owning file; every route names its handler.", ""]
    by_file = {}
    for a in apis:
        by_file.setdefault(a["handler_path"] or "(unbound)", []).append(a)
    for f in sorted(by_file):
        rows = by_file[f]
        body.append(f"## `{f}`")
        if f != "(unbound)":
            mod = con.execute("SELECT slug FROM module_files mf JOIN modules m ON m.id=mf.module_id "
                              "WHERE mf.project_id=? AND mf.path=? LIMIT 1", (pid, f)).fetchone()
            if mod:
                body.append(f"*module: [[{pid}/modules/{mod['slug'].title()}|{mod['slug']}]]*")
        body.append("")
        for a in rows[:40]:
            hs = (a["handler_symbol"] or "").split("\n")[0].strip()
            if len(hs) > 50 or "(" in hs:
                m = _re.match(r"[A-Za-z_$][\w$]*", hs)
                hs = m.group(0) if m else ""
                hs = f"`{hs}`" if hs else ""
            sym = f" → {hs}" if hs else ""
            d = f" [{a['direction']}]" if a["direction"] and a["direction"] != "server" else ""
            body.append(f"- **{a['method']}** `{a['route']}`{sym}{d}")
        if len(rows) > 40:
            body.append(f"- …and {len(rows)-40} more")
        body.append("")
    w(P / "API Surface.md", "\n".join(body))
    count += 1

    # ---------- DATABASE ----------
    ents = con.execute("""SELECT name, kind, file_path FROM db_entities
                          WHERE project_id=? ORDER BY kind, name""", (pid,)).fetchall()
    body = [fm(f"{pid} db", "[database/project]"),
            f"# {prow['name']} — Database", "", f"{len(ents)} entities.", ""]
    by_kind = {}
    for e in ents:
        by_kind.setdefault(e["kind"] or "table", []).append(e)
    order = ["table", "view", "type", "function", "bucket", "model"]
    for kind in sorted(by_kind, key=lambda k: (order.index(k) if k in order else 99, k)):
        rows = by_kind[kind]
        body += [f"## {kind} ({len(rows)})", ""]
        for e in rows[:120]:
            body.append(f"- **{e['name']}** — `{e['file_path']}`")
        if len(rows) > 120:
            body.append(f"- …and {len(rows)-120} more")
        body.append("")
    rls = con.execute("""SELECT name, path FROM symbols WHERE project_id=? AND kind='rls_policy'
                         ORDER BY path""", (pid,)).fetchall()
    if rls:
        body += ["## RLS policies (row-level security)", "",
                 "Defense-in-depth check: app-layer tenancy + these policies must BOTH hold.", ""]
        body += [f"- `{r['name']}` — `{r['path']}`" for r in rls[:60]]
        if len(rls) > 60:
            body.append(f"- …and {len(rls)-60} more")
        body.append("")
    w(P / "Database.md", "\n".join(body))
    count += 1

    # ---------- FLOWS ----------
    flows = con.execute("SELECT * FROM flows WHERE project_id=?", (pid,)).fetchall()
    body = [fm(f"{pid} flows", "[flows/project]"),
            f"# {prow['name']} — Product Flows", "",
            "End-to-end behaviors as verified from source. Files are the evidence trail.", ""]
    for f in flows:
        body.append(f"## {f['name']}")
        if f["trigger"]:
            body.append(f"**Trigger:** {f['trigger']}")
        conf = f" · confidence: {f['confidence']}" if f["confidence"] else ""
        body.append(f"*[[{pid}]]{conf}*")
        if f["steps_md"]:
            body.append("\n" + str(f["steps_md"])[:3000])
        try:
            fls = json.loads(f["files_json"] or "[]") if isinstance(f["files_json"], str) else []
        except Exception:
            fls = []
        if fls:
            body += ["", "**Files:**"]
            body += [f"- `{x}`" for x in fls[:20]]
        body.append("")
    if not flows:
        body.append("_no flows recorded_")
    w(P / "Flows.md", "\n".join(body))
    count += 1

    # ---------- TEST MAP ----------
    tests = con.execute("SELECT path, name, kind, targets_json FROM tests WHERE project_id=?",
                        (pid,)).fetchall()
    kinds = {}
    for t in tests:
        kinds.setdefault(t["kind"] or "unit", []).append(t)
    body = [fm(f"{pid} tests", "[tests/project]"),
            f"# {prow['name']} — Test Map", "", f"{len(tests)} test files.", ""]
    body += ["| Kind | Count |", "|---|---|"]
    body += [f"| {k} | {len(v)} |" for k, v in sorted(kinds.items())]
    body.append("")
    for kind in ("e2e", "integration", "unit"):
        rows = kinds.get(kind, [])
        if not rows:
            continue
        body += [f"## {kind} ({len(rows)})", ""]
        for t in rows[:50]:
            n_t = len(json.loads(t["targets_json"] or "[]"))
            body.append(f"- `{t['path']}`" + (f" — covers {n_t} targets" if n_t else ""))
        if len(rows) > 50:
            body.append(f"- …and {len(rows)-50} more")
        body.append("")
    # which source areas lack any mapped test?
    tested_targets = set()
    for t in tests:
        try:
            tested_targets |= set(json.loads(t["targets_json"] or "[]"))
        except Exception:
            pass
    untested = [r["path"] for r in con.execute(
        """SELECT path FROM files WHERE project_id=? AND is_test=0 AND is_entry=0
           AND lang IN ('ts','tsx','js','py','go')
           AND importance > 0.5 ORDER BY importance DESC LIMIT 400""", (pid,))
        if not any(t.endswith(r["path"].rsplit("/",1)[-1].rsplit(".",1)[0]) or
                   r["path"].rsplit("/",1)[-1].rsplit(".",1)[0] in t for t in tested_targets)]
    if untested:
        body += ["## High-importance code with no obvious mapped test", "",
                 "_Heuristic (name/import match). Verify before treating as gaps._", ""]
        body += [f"- `{x}`" for x in untested[:25]]
        body.append("")
    w(P / "Test Map.md", "\n".join(body))
    count += 1

    # ---------- CODE MAP ----------
    import collections
    dirs = collections.Counter()
    for r in con.execute("SELECT path FROM files WHERE project_id=?", (pid,)):
        top = r["path"].split("/")[0]
        dirs[top] += 1
    body = [fm(f"{pid} code map", "[codemap/project]"),
            f"# {prow['name']} — Code Map", "", "## Directory layout (indexed files)", ""]
    for d, c in dirs.most_common(30):
        body.append(f"- `{d}/` — {c} files")
    entries = con.execute("""SELECT path, loc FROM files WHERE project_id=? AND is_entry=1
                             ORDER BY importance DESC LIMIT 15""", (pid,)).fetchall()
    if entries:
        body += ["", "## Entry points", ""]
        body += [f"- `{e['path']}`" for e in entries]
    top_syms = con.execute("""SELECT name, kind, path, line_start, importance FROM symbols
                              WHERE project_id=? AND parent IS NULL
                              ORDER BY importance DESC LIMIT 30""", (pid,)).fetchall()
    body += ["", "## Most-connected symbols (fan-in leaders)", "",
             "| Symbol | Kind | Location |", "|---|---|---|"]
    for s in top_syms:
        body.append(f"| `{s['name']}` | {s['kind']} | `{s['path']}:{s['line_start']}` |")
    hot_files = con.execute("""SELECT path, importance, loc FROM files WHERE project_id=?
                               AND is_test=0 ORDER BY importance DESC LIMIT 25""", (pid,)).fetchall()
    body += ["", "## Highest-importance files", ""]
    body += [f"- `{h['path']}` ({h['loc'] or '?'} loc)" for h in hot_files]
    w(P / "Code Map.md", "\n".join(body))
    count += 1

    # ---------- HISTORY & HOTSPOTS ----------
    commits = con.execute("""SELECT sha, date, subject, category FROM commits
                             WHERE project_id=? ORDER BY date DESC""", (pid,)).fetchall()
    cats = collections.Counter(c["category"] or "other" for c in commits)
    hotspot = con.execute("""SELECT cf.path, COUNT(*) x FROM commit_files cf
                             WHERE cf.project_id=? GROUP BY cf.path ORDER BY x DESC LIMIT 20""",
                          (pid,)).fetchall()
    fixes = [c for c in commits if c["category"] == "fix"][:20]
    body = [fm(f"{pid} history", "[history/project]"),
            f"# {prow['name']} — History & Hotspots", "",
            f"{len(commits)} mined commits.", ""]
    if cats:
        body += ["## Commit mix", "", "| Category | Count |", "|---|---|"]
        body += [f"| {k} | {v} |" for k, v in cats.most_common()]
        body.append("")
    if hotspot:
        body += ["## Hotspots (most-changed files — treat changes here carefully)", ""]
        body += [f"- `{h['path']}` — touched {h['x']}×" for h in hotspot]
        body.append("")
    if fixes:
        body += ["## Recent fixes (past pitfalls live here)", ""]
        body += [f"- `{c['sha'][:10]}` {c['date']} {str(c['subject'])[:110]}" for c in fixes]
        body.append("")
    w(P / "History & Hotspots.md", "\n".join(body))
    count += 1
    return count


def generate(con):
    from cortex.session import quality_report
    n = {"files": 0}
    projs = [r["id"] for r in con.execute("SELECT id FROM projects ORDER BY id")]

    # ---- Home
    lines = ["# Project Cortex", "",
             "> Index deeply once, retrieve narrowly forever.", "",
             "## Projects"]
    for pid in projs:
        p, s = project_status(con, pid)
        fresh = "fresh" if not s["behind"] else f"behind ~{s['behind']} commits"
        lines.append(f"- [[{pid}/Home|{p['name']}]] — {s['files']} files, {s['symbols']} symbols, {fresh}")
    lines += ["", "## Cross-cutting", "- [[Global/Engineering Principles]]",
              "- [[Global/Cross Project Patterns]]", "- [[Decisions/Decision Index]]",
              "- [[Episodes]]", "- [[Cortex Quality]]", "- [[Knowledge Health]]",
              "", "## Usage", "`cortex context \"<task>\"` · `cortex impact \"<file>\"` · `cortex update`"]
    w(VAULT / "Home.md", fm("Project Cortex", "[home/cortex]") + "\n".join(lines) + "\n")
    n["files"] += 1

    # ---- learning loop pages
    eps = con.execute("""SELECT * FROM episodes ORDER BY id DESC LIMIT 40""").fetchall()
    body = [fm("Episodes", "[episodes/cortex]"),
            "# Engineering Episodes", "",
            "Validated knowledge extracted from completed tasks. Query via "
            "`cortex episode list` / packets' PAST TASK LESSONS.", ""]
    for e in eps:
        flags = []
        if e["status"] != "active":
            flags.append(e["status"])
        if e["outcome"] == "failed":
            flags.append("FAILED ATTEMPT — do not repeat")
        tag = f" ({', '.join(flags)})" if flags else ""
        body.append(f"## {e['task'][:100]}{tag}")
        body.append(f"`{e['project_id']}` · {e['outcome']} · {e['confidence']}"
                    + (f" · `{e['commit_sha']}`" if e["commit_sha"] else ""))
        for k, lbl in (("problem", "Problem"), ("root_cause", "Root cause"),
                       ("lessons", "Lessons"), ("failed_approaches", "Failed approaches")):
            if e[k]:
                body.append(f"- **{lbl}:** {e[k][:400]}")
        body.append("")
    w(VAULT / "Episodes.md", "\n".join(body))
    n["files"] += 1

    q = quality_report(con)
    body = [fm("Cortex Quality", "[quality/cortex]"),
            "# Cortex Quality", "",
            "| Metric | Value |", "|---|---|",
            f"| Sessions started / completed | {q['sessions_started']} / {q['sessions_completed']} |",
            f"| Episodes (active/total) | {q['episodes_active']} / {q['episodes_total']} |",
            f"| Failed-task lessons kept | {q['episodes_failed_lessons']} |",
            f"| Generated memories | {q['memories_generated']} |",
            f"| Primary-file hit rate (measured) | {q['primary_file_hit_rate']} |",
            f"| Suggestion recall (measured) | {q['suggestion_recall']} |",
            f"| Test-recommendation hit rate | {q['test_hit_rate']} |", ""]
    w(VAULT / "Cortex Quality.md", "\n".join(body))
    n["files"] += 1

    stale = con.execute("""SELECT scope, project_id, title FROM memories
                           WHERE stale=1 OR status IN ('obsolete','uncertain','superseded')
                           ORDER BY project_id""").fetchall()
    uncertain_eps = con.execute(
        "SELECT id, project_id, task FROM episodes WHERE status IN ('uncertain','obsolete')").fetchall()
    body = [fm("Knowledge Health", "[health/cortex]"),
            "# Knowledge Health", "", "## Stale / flagged memories"]
    body += [f"- [{m['scope']}] {m['project_id'] or 'GLOBAL'}: {m['title']}" for m in stale] or ["- none"]
    body += ["", "## Uncertain/obsolete episodes (contradiction candidates)"]
    body += [f"- #{e['id']} {e['project_id']}: {e['task'][:90]}" for e in uncertain_eps] or ["- none"]
    w(VAULT / "Knowledge Health.md", "\n".join(body) + "\n")
    n["files"] += 1

    for pid in projs:
        p, s = project_status(con, pid)
        # ---- project hub page
        body = [fm(pid, "[project]"),
                f"# {p['name']}", "",
                f"**Path:** `{p['path']}`  ",
                f"**Kind:** {p['kind']} | **Languages:** {p['languages']} | **Frameworks:** {p['frameworks']}", "",
                f"**HEAD:** `{(p['git_head'] or '')[:12]}` | **Brain:** `{(p['indexed_commit'] or '')[:12]}` | "
                f"{'FRESH' if not s['behind'] else f'BEHIND ~{s[chr(98)+chr(101)]} commits'}"
                + (f" | {s['dirty_files'] if 'dirty_files' in s.keys() else ''}" if False else ""), ""]
        stats = (f"| Files | Symbols | Modules | Flows | APIs | DB | Tests | Decisions | Memories |\n"
                 f"|---|---|---|---|---|---|---|---|---|\n"
                 f"| {s['files']} | {s['symbols']} | {s['modules']} | {s['flows']} | {s['apis']} | "
                 f"{s['db']} | {s['tests']} | {s['decisions']} | {s['memories']} ({s['stale_mem']} stale) |")
        sub = ["API Surface", "Code Map", "Database", "Flows", "History & Hotspots", "Test Map"]
        body += [stats, "", "## Examiner pages"]
        body += [f"- [[{pid}/{s}|{s}]]" for s in sub]
        body += ["", "## Pitfalls & rules (memories)"]
        for mem in con.execute("""SELECT title,confidence,stale FROM memories
                                  WHERE project_id=? AND scope IN ('pitfall','business_rule','history')
                                  ORDER BY scope LIMIT 15""", (pid,)):
            st = " ⚠️stale" if mem["stale"] else ""
            body.append(f"- {mem['title']} [{mem['confidence']}]{st}")
        body += ["", "## Modules"]
        mods = con.execute("SELECT * FROM modules WHERE project_id=? ORDER BY slug", (pid,)).fetchall()
        for m in mods:
            body.append(f"- [[{pid}/modules/{m['slug'].title()}|{m['name']}]] — {(m['purpose'] or '')[:100]} [{m['confidence']}]")
        body += ["", "## Flows"]
        for f in con.execute("SELECT * FROM flows WHERE project_id=?", (pid,)):
            body.append(f"- **{f['name']}** — {(f['trigger'] or '')[:120]}")
        body += ["", "## Key knowledge"]
        for mem in con.execute("""SELECT title,confidence,stale,rowid FROM memories
                                  WHERE project_id=? AND scope IN ('architecture','project','history')
                                  ORDER BY scope""", (pid,)):
            stale = " ⚠️stale" if mem["stale"] else ""
            body.append(f"- {mem['title']} [{mem['confidence']}]{stale}")
        w(VAULT / "Projects" / f"{pid}.md", "\n".join(body) + "\n")
        n["files"] += 1

        # ---- per-project landing alias for wikilinks [[<pid>/Home]]
        w(VAULT / "Projects" / pid / "Home.md",
          fm(pid, "[project]") + f"# {p['name']}\n\nSee [[{pid}]].\n")
        n["files"] += 1

        n["files"] += _deep_pages(con, pid, p)

        # ---- module notes
        for m in mods:
            mf = [r["path"] for r in con.execute(
                "SELECT path FROM module_files WHERE module_id=? ORDER BY path LIMIT 40", (m["id"],))]
            note = [fm(m["slug"], "[module]"),
                    f"# {m['name']}", "",
                    f"**Project:** [[{pid}]] | **Confidence:** {m['confidence']} | **verified@** `{(m['verified_at_commit'] or '')[:12]}`",
                    f"**Owns:** `{m['path_prefixes']}`", "",
                    m["body_md"] or "", ""]
            if mf:
                note += ["## Files (" + str(len(mf)) + "+)", ""]
                note += [f"- `{x}`" for x in mf[:25]]
            apis = con.execute("""SELECT DISTINCT method,route FROM apis a JOIN module_files mf2 ON mf2.path=a.handler_path
                                  WHERE mf2.module_id=? LIMIT 15""", (m["id"],)).fetchall()
            if apis:
                note += ["", "## API surface", ""]
                note += [f"- `{a['method']} {a['route']}`" for a in apis]
            w(VAULT / "Projects" / pid / "modules" / f"{m['slug'].title()}.md", "\n".join(note) + "\n")
            n["files"] += 1

    # ---- Global knowledge pages
    gmem = con.execute("SELECT * FROM memories WHERE project_id IS NULL").fetchall()
    gp = VAULT / "Global" / "Engineering Principles.md"
    content = fm("principles", "[global]") + "# Engineering Principles\n\n"
    for m in gmem:
        content += f"## {m['title']}\n\n{m['body_md']}\n\n"
    w(gp, content)
    n["files"] += 1

    # cross-project pattern detection: shared concepts across projects via memory titles+keywords
    concepts = {}
    KW = ["authentication", "auth", "rls", "tenant", "rag", "knowledge", "payment", "audit",
          "agent", "queue", "worker", "webhook", "rate limit", "migration", "odoo", "whatsapp",
          "voice", "llm", "gemini", "stripe", "billing", "onboarding", "rbac", "permission"]
    for k in KW:
        hits = []
        for r in con.execute("""SELECT DISTINCT project_id, title FROM memories
                                WHERE (lower(body_md) LIKE ? OR lower(title) LIKE ?)
                                AND project_id IS NOT NULL""", (f"%{k}%", f"%{k}%")):
            hits.append((r["project_id"], r["title"]))
        byproj = {}
        for pp, t in hits:
            byproj.setdefault(pp, t)
        if len(byproj) >= 2:
            concepts[k] = byproj
    cp = VAULT / "Global" / "Cross Project Patterns.md"
    content = fm("patterns", "[global]") + ("# Cross-Project Patterns\n\nConcepts appearing in multiple projects.\n")
    for k, byproj in sorted(concepts.items(), key=lambda kv: -len(kv[1])):
        content += f"\n## {k.title()} — {len(byproj)} projects\n"
        for pp, title in list(byproj.items())[:6]:
            content += f"- [[{pp}]]: {title[:90]}\n"
    w(VAULT / "Global" / "Cross Project Patterns.md", content)
    n["files"] += 1

    # ---- Decision index
    dp = VAULT / "Decisions" / "Decision Index.md"
    content = fm("decisions", "[decisions]") + "# Decision Index\n\n"
    for pid in projs:
        rows = con.execute("SELECT title,commit_sha,source FROM decisions WHERE project_id=?", (pid,)).fetchall()
        if rows:
            content += f"\n## [[{pid}]]\n"
            for r in rows:
                sha = f" (`{r['commit_sha']}`)" if r["commit_sha"] else ""
                content += f"- {r['title'][:120]}{sha}\n"
    w(dp, content)
    n["files"] += 1

    return n


def json_files(_):
    return ""


if __name__ == "__main__":
    con = connect()
    print(generate(con))
