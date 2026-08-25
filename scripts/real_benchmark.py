"""Generate REAL_WORLD_BENCHMARK.md from measured task-session telemetry.

Only measured data appears here. Simulated figures live in
TOKEN_EFFICIENCY_BENCHMARK.md and are never mixed in.
"""
import json, pathlib, sys, datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from cortex.db import connect  # noqa: E402
from cortex.session import quality_report  # noqa: E402


def main():
    con = connect()
    q = quality_report(con)
    rows = list(con.execute(
        """SELECT * FROM task_sessions WHERE completed_at IS NOT NULL ORDER BY id"""))
    ctx_chars = [r["context_chars"] for r in rows if r["context_chars"]]
    med = lambda xs: sorted(xs)[len(xs) // 2] if xs else None

    out = [f"# Real-World Benchmark", "",
           f"_Generated {datetime.date.today()} from `task_sessions` — MEASURED data only._",
           "", "## Method",
           "",
           "Every real task run through `cortex task start` / `cortex task complete` records:",
           "context packet size at start, files Cortex suggested, files actually touched",
           "(git diff attributed to the session), and precision/recall of suggestions.",
           "Baseline (no-cortex discovery cost) is NOT fabricated: until we log unaided"
           " sessions side-by-side, only the Cortex column exists. The simulated ~94%"
           " reduction in TOKEN_EFFICIENCY_BENCHMARK.md remains clearly labeled simulated.", "",
           "## Aggregate (measured)", "",
           "| Metric | Value |", "|---|---|",
           f"| Tasks measured | {q['sessions_completed']} |",
           f"| Median context packet | {med(ctx_chars) or 0:,} chars (~{(med(ctx_chars) or 0)//4:,} tokens) |",
           f"| Primary-file hit rate | {q['primary_file_hit_rate']} |",
           f"| Suggestion recall | {q['suggestion_recall']} |",
           f"| Test-recommendation hit rate | {q['test_hit_rate']} |",
           f"| Episodes captured | {q['episodes_active']} active / {q['episodes_total']} total |", "",
           "## Per-task log", "",
           "| # | project | outcome | suggested | touched | precision | recall | context tok~ |",
           "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        m = json.loads(r["metrics_json"] or "{}")
        out.append(f"| #{r['id']} | {r['project_id'] or '?'} | {r['outcome']} "
                   f"| {m.get('files_suggested', '-')} | {m.get('files_touched', '-')} "
                   f"| {m.get('primary_precision', '-')} | {m.get('suggestion_recall', '-')} "
                   f"| {(r['context_chars'] or 0)//4:,} |")
    p = pathlib.Path(__file__).resolve().parents[1] / "REAL_WORLD_BENCHMARK.md"
    p.write_text("\n".join(out) + "\n")
    print(f"wrote {p} ({q['sessions_completed']} measured tasks)")


if __name__ == "__main__":
    main()
