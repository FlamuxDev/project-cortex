---
cortex-generated: true
title: hr-attendance-custom-extensions
tags: [module]
---

# HR Attendance Custom Extensions

**Project:** [[shamsieh]] | **Confidence:** inferred | **verified@** `ad14342a33e9`
**Owns:** `hr_attendance_custom_ext/`

purpose: Attendance core: fingerprint sync (Hikvision + ZKTeco), face attendance enrollment/matching, daily status views, live status, unworked-time tracking.
path_prefixes: hr_attendance_custom_ext/
key_files: models/fingerprint_device.py (`_cron_sync_all`, ingest endpoint target), models/fingerprint_device_log.py (`_cron_process_pending`, `_cron_purge_raw_payload`), models/hr_attendance_daily_status.py (`_cron_generate_daily_status`, `_cron_backfill_current_month_unworked_time`), models/hr_attendance.py (`_cron_recompute_status`, `_cron_flag_missing_checkouts`), services/zkteco.py, static/src JS dialogs
entrypoints: crons above; controllers for public presence-status reads; post_init_hook
responsibilities: normalize device events into `hr.attendance`; daily status rows; late/early computation; missing-checkout flagging; billable unworked minutes; PIN/face check-in alignment with live status.
invariants: raw device payloads purged after processing; public exposure of attendance fields limited to what officers need (commit 330c17da).
pitfalls: recursion bug in the custom attendance action override was real (86f04052); Owl prop binding broke dialogs (9b558a15); `tests_disabled/` directory exists — coverage intentionally off.
confidence: high

## Files (40+)

- `hr_attendance_custom_ext/__init__.py`
- `hr_attendance_custom_ext/__manifest__.py`
- `hr_attendance_custom_ext/controllers/__init__.py`
- `hr_attendance_custom_ext/controllers/face_attendance.py`
- `hr_attendance_custom_ext/controllers/hikvision_event.py`
- `hr_attendance_custom_ext/controllers/hr_attendance.py`
- `hr_attendance_custom_ext/controllers/zkteco_adms.py`
- `hr_attendance_custom_ext/controllers/zkteco_punch.py`
- `hr_attendance_custom_ext/hooks.py`
- `hr_attendance_custom_ext/migrations/19.0.1.2.0/post-migrate.py`
- `hr_attendance_custom_ext/migrations/19.0.1.3.24/post-migrate.py`
- `hr_attendance_custom_ext/migrations/19.0.1.3.28/post-migrate.py`
- `hr_attendance_custom_ext/migrations/19.0.1.3.29/post-migrate.py`
- `hr_attendance_custom_ext/migrations/19.0.1.3.31/pre-migrate.py`
- `hr_attendance_custom_ext/migrations/19.0.1.3.34/post-migrate.py`
- `hr_attendance_custom_ext/migrations/19.0.1.3.34/pre-migrate.py`
- `hr_attendance_custom_ext/migrations/19.0.1.3.48/post-migrate.py`
- `hr_attendance_custom_ext/migrations/19.0.1.4.1/pre-migrate.py`
- `hr_attendance_custom_ext/migrations/19.0.1.4.2/post-migrate.py`
- `hr_attendance_custom_ext/migrations/19.0.1.4.3/post-migrate.py`
- `hr_attendance_custom_ext/models/__init__.py`
- `hr_attendance_custom_ext/models/attendance_calendar_mixin.py`
- `hr_attendance_custom_ext/models/face_attendance_log.py`
- `hr_attendance_custom_ext/models/fingerprint_attendance_policy.py`
- `hr_attendance_custom_ext/models/fingerprint_device.py`
