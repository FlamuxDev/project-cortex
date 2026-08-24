---
cortex-generated: true
title: scheduled-jobs
tags: [module]
---

# Scheduled jobs

**Project:** [[mythos]] | **Confidence:** inferred | **verified@** `15e9faf0b5db`
**Owns:** `cron/,tools/cronjob_tools.py,safa_cli/cron.py`

purpose: natural-language scheduled automations delivered to any platform.
path_prefixes: cron/, tools/cronjob_tools.py, safa_cli/cron.py
key_files: cron/jobs.py, cron/scheduler.py
entrypoints: cronjob tool; `safa cron list/add/edit/…`; `/cron` slash
responsibilities: duration/every/5-field-cron/ISO parsing; per-job model/provider/script/context_from/workdir/multi-platform delivery
invariants: 3-minute hard interrupt per cron session; tick lock file prevents duplicate ticks across processes; catchup window = half period clamped 120s–2h; skip_memory=True
confidence: high

## Files (19+)

- `cron/__init__.py`
- `cron/jobs.py`
- `cron/scheduler.py`
- `safa_cli/cron.py`
- `tests/cron/__init__.py`
- `tests/cron/test_codex_execution_paths.py`
- `tests/cron/test_compute_next_run_last_run_at.py`
- `tests/cron/test_cron_context_from.py`
- `tests/cron/test_cron_inactivity_timeout.py`
- `tests/cron/test_cron_no_agent.py`
- `tests/cron/test_cron_prompt_injection_skill.py`
- `tests/cron/test_cron_script.py`
- `tests/cron/test_cron_workdir.py`
- `tests/cron/test_file_permissions.py`
- `tests/cron/test_jobs.py`
- `tests/cron/test_rewrite_skill_refs.py`
- `tests/cron/test_scheduler.py`
- `tests/cron/test_scheduler_mcp_init.py`
- `tools/cronjob_tools.py`
