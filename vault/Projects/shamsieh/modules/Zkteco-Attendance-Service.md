---
cortex-generated: true
title: zkteco-attendance-service
tags: [module]
---

# zkteco_attendance_service

**Project:** [[shamsieh]] | **Confidence:** inferred | **verified@** `ad14342a33e9`
**Owns:** `zkteco_attendance_service/`

purpose: Poll ZKTeco terminals from a LAN PC and push events into Odoo.
path_prefixes: zkteco_attendance_service/
key_files: app/main.py (imports `zkteco` client from hr_attendance_custom_ext/services via sys.path insertion)
entrypoints: `python -m app.main`
responsibilities: pull new punches (pyzk), normalize, XML-RPC push to `fingerprint.device.ingest_external_attendance_events`.
pitfalls: reaches into the Odoo module tree of a *sibling checkout* (`extra_addons/hr_attendance_custom_ext/services`) — deployment layout coupling.
confidence: medium-high

## Files (2+)

- `zkteco_attendance_service/app/__init__.py`
- `zkteco_attendance_service/app/main.py`
