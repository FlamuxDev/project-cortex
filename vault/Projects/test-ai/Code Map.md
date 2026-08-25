---
cortex-generated: true
title: test-ai code map
tags: [codemap/project]
---

# TEST AI — Code Map

## Directory layout (indexed files)

- `agent/` — 37 files
- `tests/` — 29 files
- `tools/` — 18 files
- `sql/` — 5 files
- `eval/` — 3 files
- `web/` — 2 files
- `production_backup_2026-08-09_03-00-02.sql/` — 1 files

## Most-connected symbols (fan-in leaders)

| Symbol | Kind | Location |
|---|---|---|
| `t` | function | `web/dashboard.js:136` |
| `n` | function | `tests/test_compile.py:177` |
| `_spec` | function | `tests/test_constraints.py:26` |
| `run` | function | `agent/cli.py:21` |
| `run` | function | `agent/refresh.py:310` |
| `run` | function | `agent/reports.py:237` |
| `run` | function | `tests/_runner.py:16` |
| `run` | function | `tools/audit_robustness.py:84` |
| `run` | function | `tools/audit_semantics.py:183` |
| `run` | function | `tools/probe.py:45` |
| `QuerySpec` | class | `agent/spec.py:41` |
| `turn` | function | `tests/test_episodes.py:15` |
| `esc` | function | `web/dashboard.js:206` |
| `Filter` | class | `agent/spec.py:28` |
| `field` | function | `agent/refresh.py:167` |
| `validate` | function | `agent/plan.py:406` |
| `log` | function | `eval/domain_sweep.py:137` |
| `normalize` | function | `agent/arabic.py:27` |
| `sheet` | function | `tests/test_session.py:35` |
| `Catalog` | class | `agent/catalog.py:76` |
| `get_catalog` | function | `agent/catalog.py:491` |
| `_sheet` | function | `tests/test_robustness.py:45` |
| `num` | function | `web/dashboard.js:212` |
| `main` | function | `eval/domain_sweep.py:126` |
| `main` | function | `eval/gen_gold.py:141` |
| `main` | function | `eval/run_eval.py:271` |
| `main` | function | `tests/test_arabic.py:170` |
| `main` | function | `tests/test_compile.py:184` |
| `main` | function | `tests/test_compile.py:331` |
| `main` | function | `tests/test_compile.py:394` |

## Highest-importance files

- `agent/api.py` (873 loc)
- `agent/db.py` (63 loc)
- `agent/config.py` (154 loc)
- `agent/logbook.py` (895 loc)
- `agent/country.py` (166 loc)
- `agent/gemini.py` (213 loc)
- `agent/health.py` (80 loc)
- `agent/whatsapp.py` (322 loc)
- `agent/constraints.py` (169 loc)
- `agent/episodes.py` (334 loc)
- `agent/institution_verify.py` (646 loc)
- `agent/intake.py` (242 loc)
- `agent/judge.py` (438 loc)
- `agent/pricing.py` (170 loc)
- `agent/refresh.py` (370 loc)
- `agent/reports.py` (299 loc)
- `agent/smalltalk.py` (95 loc)
- `agent/voice.py` (344 loc)
- `web/dashboard.js` (611 loc)
- `agent/__init__.py` (1 loc)
- `agent/answer.py` (470 loc)
- `agent/applog.py` (61 loc)
- `agent/arabic.py` (172 loc)
- `agent/catalog.py` (496 loc)
- `agent/cli.py` (113 loc)