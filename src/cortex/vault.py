"""Generate the Obsidian vault from the cortex DB.

Generated files carry frontmatter `cortex-generated: true`; anything else is
treated as human-curated and never overwritten.
"""
from __future__ import annotations
import pathlib, re, sys

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
    w(VAULT / "Home.md", "\n".join(lines) + "\n")
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
        body += [stats, "", "## Modules"]
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

        # ---- module notes
        for m in mods:
            mf = [r["path"] for r in con.execute(
                "SELECT path FROM module_files WHERE module_id=? ORDER BY path LIMIT 40", (m["id"],))]
            flows_here = [r["name"] for r in con.execute(
                "SELECT name FROM flows WHERE project_id=?", (pid,))
                if any(x and x in json_files(r) for x in [])]
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
