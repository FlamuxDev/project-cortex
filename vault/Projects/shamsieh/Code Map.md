---
cortex-generated: true
title: shamsieh code map
tags: [codemap/project]
---

# shamsieh — Code Map

## Directory layout (indexed files)

- `hr_attendance_custom_ext/` — 74 files
- `hr_overtime_management/` — 52 files
- `hr_holidays_custom_ext/` — 42 files
- `botify_agent/` — 24 files
- `project_custom_ext/` — 20 files
- `hr_loans_advances/` — 17 files
- `crm_custom_ext/` — 16 files
- `shams_todo_groups/` — 13 files
- `shamsieh_i18n_ar/` — 12 files
- `hikvision_attendance_service/` — 7 files
- `website_lead_api/` — 7 files
- `scripts/` — 4 files
- `hr_overtime_payroll/` — 3 files
- `hr_payroll_custom_ext/` — 2 files
- `hr_payroll_jo_custom_ext/` — 2 files
- `zkteco_attendance_service/` — 2 files

## Entry points

- `hikvision_attendance_service/app/main.py`
- `botify_agent/controllers/main.py`
- `website_lead_api/controllers/main.py`
- `zkteco_attendance_service/app/main.py`

## Most-connected symbols (fan-in leaders)

| Symbol | Kind | Location |
|---|---|---|
| `error` | function | `botify_agent/controllers/_shared.py:108` |
| `add_heading` | function | `hikvision_attendance_service/doc/generate_documentation.py:64` |
| `add_bullet` | function | `hikvision_attendance_service/doc/generate_documentation.py:92` |
| `add_bullet` | function | `hr_overtime_management/doc/generate_documentation_pdf.py:84` |
| `add_heading` | function | `hr_overtime_management/doc/generate_full_documentation.py:65` |
| `add_bullet` | function | `hr_overtime_management/doc/generate_full_documentation.py:96` |
| `add_body` | function | `hikvision_attendance_service/doc/generate_documentation.py:84` |
| `add_body` | function | `hr_overtime_management/doc/generate_full_documentation.py:87` |
| `add_table` | function | `hikvision_attendance_service/doc/generate_documentation.py:101` |
| `add_table` | function | `hr_overtime_management/doc/generate_documentation_pdf.py:87` |
| `add_table` | function | `hr_overtime_management/doc/generate_full_documentation.py:106` |
| `xmlid` | function | `hr_overtime_management/doc/_fix_employee_access_odoo19.py:11` |
| `add_p` | function | `hr_overtime_management/doc/generate_documentation_pdf.py:81` |
| `_dash_label` | function | `shams_todo_groups/models/todo_dashboard.py:73` |
| `main` | function | `hikvision_attendance_service/doc/generate_documentation.py:322` |
| `main` | function | `hr_overtime_management/doc/_fix_corrupted_views_odoo19.py:29` |
| `main` | function | `hr_overtime_management/doc/_fix_employee_access_odoo19.py:154` |
| `main` | function | `hr_overtime_management/doc/generate_full_documentation.py:670` |
| `main` | function | `scripts/build_odoo_ar_po.py:326` |
| `main` | function | `scripts/extract_i18n_strings.py:60` |
| `main` | function | `scripts/generate_ar_po.py:916` |
| `main` | function | `scripts/test_hikvision.py:49` |
| `main` | function | `zkteco_attendance_service/app/main.py:98` |
| `json_response` | function | `botify_agent/controllers/_shared.py:100` |
| `Occurrence` | class | `scripts/build_odoo_ar_po.py:61` |
| `add_h1` | function | `hr_overtime_management/doc/generate_documentation_pdf.py:75` |
| `_employee_no` | function | `hikvision_attendance_service/app/hikvision_parser.py:254` |
| `_verify_mode` | function | `hikvision_attendance_service/app/hikvision_parser.py:262` |
| `_verify_mode` | function | `hr_attendance_custom_ext/services/hikvision_connector.py:51` |
| `_employee_no` | function | `hr_attendance_custom_ext/services/hikvision_http_push.py:57` |

## Highest-importance files

- `hikvision_attendance_service/app/main.py` (417 loc)
- `botify_agent/controllers/main.py` (373 loc)
- `website_lead_api/controllers/main.py` (364 loc)
- `zkteco_attendance_service/app/main.py` (114 loc)
- `botify_agent/static/src/js/botify_client_action.js` (526 loc)
- `hr_attendance_custom_ext/static/src/components/face_check_dialog/face_check_dialog.js` (108 loc)
- `hr_attendance_custom_ext/static/src/components/home_pin_dialog/home_pin_dialog.js` (73 loc)
- `hr_overtime_management/static/src/overtime_error_handler.js` (100 loc)
- `project_custom_ext/static/src/action_restore_fix.js` (40 loc)
- `project_custom_ext/static/src/compact_hours_field.js` (48 loc)
- `project_custom_ext/static/src/project_notifications.js` (110 loc)
- `botify_agent/__init__.py` (3 loc)
- `botify_agent/__manifest__.py` (53 loc)
- `botify_agent/controllers/__init__.py` (3 loc)
- `botify_agent/controllers/_shared.py` (156 loc)
- `botify_agent/controllers/grant.py` (204 loc)
- `botify_agent/models/__init__.py` (7 loc)
- `botify_agent/models/botify_canonical.py` (79 loc)
- `botify_agent/models/botify_delegation.py` (58 loc)
- `botify_agent/models/botify_nonce.py` (53 loc)
- `botify_agent/models/botify_policy.py` (250 loc)
- `botify_agent/models/botify_security.py` (151 loc)
- `botify_agent/models/res_config_settings.py` (128 loc)
- `crm_custom_ext/__init__.py` (3 loc)
- `crm_custom_ext/__manifest__.py` (41 loc)