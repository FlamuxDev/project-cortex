---
cortex-generated: true
title: hikvision-attendance-service
tags: [module]
---

# hikvision_attendance_service

**Project:** [[shamsieh]] | **Confidence:** inferred | **verified@** `ad14342a33e9`
**Owns:** `hikvision_attendance_service/`

purpose: Receive Hikvision attendance/access webhooks, persist durably, forward into Odoo.
path_prefixes: hikvision_attendance_service/
key_files: app/main.py, app/hikvision_parser.py, app/db.py (SQLite EventStore + retry queue), app/odoo_client.py (XML-RPC over `/xmlrpc/2/common|object`), app/config.py (env-driven, SQLITE_PATH default hikvision_bridge.db)
entrypoints: uvicorn app; POST/GET `/hikvision/attendance`, `/health`, `/odoo/ping`
responsibilities: multipart event parsing (employee_no, sub_event_type, verify_mode), punch-type normalization, idempotent forwarding with retry worker, log-noise suppression.
invariants: nothing is dropped silently — failed forwards sit in SQLite until retried.
pitfalls: runs outside Odoo.sh, so its config/secrets live in env files not in git.
confidence: high

## Files (7+)

- `hikvision_attendance_service/app/__init__.py`
- `hikvision_attendance_service/app/config.py`
- `hikvision_attendance_service/app/db.py`
- `hikvision_attendance_service/app/hikvision_parser.py`
- `hikvision_attendance_service/app/main.py`
- `hikvision_attendance_service/app/odoo_client.py`
- `hikvision_attendance_service/doc/generate_documentation.py`

## API surface

- `GET /hikvision/attendance`
- `POST /hikvision/attendance`
- `GET /health`
- `GET /odoo/ping`
