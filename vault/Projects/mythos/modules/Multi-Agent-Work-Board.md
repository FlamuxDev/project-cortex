---
cortex-generated: true
title: multi-agent-work-board
tags: [module]
---

# Multi-agent work board

**Project:** [[mythos]] | **Confidence:** inferred | **verified@** `15e9faf0b5db`
**Owns:** `safa_cli/kanban_db.py,safa_cli/kanban.py,tools/kanban_tools.py,plugins/kanban/`

purpose: durable SQLite board coordinating multiple profiles/worker agents.
path_prefixes: safa_cli/kanban_db.py, safa_cli/kanban.py, tools/kanban_tools.py, plugins/kanban/
key_files: safa_cli/kanban_db.py (tables tasks, task_links, task_comments, task_events, task_runs, kanban_notify_subs), plugins/kanban/dashboard/, systemd unit mythos-kanban-dispatcher.service
entrypoints: `safa kanban <verb>`; dispatcher inside gateway (kanban.dispatch_in_gateway:true) or standalone service
responsibilities: atomically claim ready tasks, spawn assigned profiles, heartbeat/watch/gc, auto-block after ~5 consecutive spawn failures
invariants: Board = hard boundary (workers get SAFA_KANBAN_BOARD pinned); tenant = soft namespace within board; kanban_* toolset hidden unless SAFA_KANBAN_TASK set
confidence: high

## Files (4+)

- `plugins/kanban/dashboard/plugin_api.py`
- `safa_cli/kanban.py`
- `safa_cli/kanban_db.py`
- `tools/kanban_tools.py`

## API surface

- `GET /board`
- `GET /tasks/{task_id}`
- `POST /tasks`
- `PATCH /tasks/{task_id}`
- `POST /tasks/{task_id}/comments`
- `POST /links`
- `DELETE /links`
- `POST /tasks/bulk`
- `GET /diagnostics`
- `POST /tasks/{task_id}/reclaim`
- `POST /tasks/{task_id}/reassign`
- `GET /config`
- `GET /home-channels`
- `POST /tasks/{task_id}/home-subscribe/{platform}`
- `DELETE /tasks/{task_id}/home-subscribe/{platform}`
