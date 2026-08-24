---
cortex-generated: true
title: iscc-attendance-sync
tags: [module]
---

# iscc_attendance_sync

**Project:** [[iscc-testing]] | **Confidence:** inferred | **verified@** `96dc8874d12b`
**Owns:** `iscc_attendance_sync/`

purpose: Pull punches from external systems (Sprinklr or generic HTTP JSON, plus a mock provider) into `hr.attendance`.
path_prefixes: iscc_attendance_sync/
key_files: models/iscc_attendance_source.py, models/iscc_attendance_punch.py, data/ir_cron_data.xml
entrypoints: cron `model._cron_sync_attendance()` (inactive by default), manual `action_sync`
responsibilities: provider abstraction (`mock|sprinklr|http_json` → `_fetch_punches_http` using `requests.get` timeout 30), employee matching by `iscc_external_attendance_id`, overnight-punch handling.
invariants: cron ships disabled with a "Sprinklr (Demo/Mock)" source row — enabling is a deliberate operator act.
pitfalls: matching by external id fails silently if the field is unpopulated [inferred from `_match_employee`].
confidence: high

## Files (7+)

- `iscc_attendance_sync/__init__.py`
- `iscc_attendance_sync/__manifest__.py`
- `iscc_attendance_sync/models/__init__.py`
- `iscc_attendance_sync/models/hr_attendance.py`
- `iscc_attendance_sync/models/hr_employee.py`
- `iscc_attendance_sync/models/iscc_attendance_punch.py`
- `iscc_attendance_sync/models/iscc_attendance_source.py`
