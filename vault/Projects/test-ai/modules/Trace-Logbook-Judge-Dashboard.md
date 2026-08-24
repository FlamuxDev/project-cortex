---
cortex-generated: true
title: trace-logbook-judge-dashboard
tags: [module]
---

# trace / logbook / judge / dashboard

**Project:** [[test-ai]] | **Confidence:** inferred | **verified@** `ec5e16f84200`
**Owns:** `agent/trace.py,agent/logbook.py,agent/judge.py,agent/reports.py,traces/,web/dashboard*`

purpose: Record every turn, classify outcomes, judge correctness from production traffic, surface it all in a six-section two-language dashboard.
path_prefixes: agent/trace.py, agent/logbook.py, agent/judge.py, agent/reports.py, traces/, web/dashboard*
key_files: agent/logbook.py (SQLite logbook.db: sessions, turns, failures, top questions, unanswered, problems), agent/judge.py (LLM-judged strata, Wilson intervals), eval/run_eval.py (166 golden cases, concurrency 5, truth from SQL)
entrypoints: /dashboard, /traces, /stats, /reports/* (admin key)
invariants: eval traffic excluded from production stats (`_scope(include_eval)`).
confidence: high

## Files (4+)

- `agent/judge.py`
- `agent/logbook.py`
- `agent/reports.py`
- `agent/trace.py`
