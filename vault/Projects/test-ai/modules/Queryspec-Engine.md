---
cortex-generated: true
title: queryspec-engine
tags: [module]
---

# QuerySpec engine

**Project:** [[test-ai]] | **Confidence:** inferred | **verified@** `ec5e16f84200`
**Owns:** `agent/spec.py,agent/plan.py,agent/compile.py,agent/constraints.py,agent/fastpath.py,agent/db.py`

purpose: Turn natural language into safe parameterized SQL via structured spec + deterministic validator/compiler.
path_prefixes: agent/spec.py, agent/plan.py, agent/compile.py, agent/constraints.py, agent/fastpath.py, agent/db.py
key_files: agent/plan.py (planner Gemini call #1 + 9-check validator with ≤1 repair), agent/compile.py (QuerySpec→SQL; NULLS LAST, coverage denominators, filter semantics), sql/02_role.sql (ai_reader read-only)
entrypoints: pipeline stages 4–7
invariants: parameterized SQL only, executed as ai_reader on ai_views with statement_timeout=3s; validator may fix once, then refuses.
pitfalls: wildcard holes and near-miss entity matching were both historical bug families (commits 3d044cd, 03166a5) — audits now hunt classes, not instances.
confidence: high

## Files (6+)

- `agent/compile.py`
- `agent/constraints.py`
- `agent/db.py`
- `agent/fastpath.py`
- `agent/plan.py`
- `agent/spec.py`
