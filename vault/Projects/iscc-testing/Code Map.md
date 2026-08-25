---
cortex-generated: true
title: iscc-testing code map
tags: [codemap/project]
---

# iscc-Testing — Code Map

## Directory layout (indexed files)

- `botify_agent/` — 12 files
- `iscc_violations/` — 9 files
- `iscc_shift/` — 8 files
- `iscc_attendance_sync/` — 7 files
- `iscc_continuous_absence/` — 6 files
- `iscc_hr_base/` — 6 files
- `iscc_leave_ext/` — 6 files
- `iscc_payroll_ext/` — 6 files
- `iscc_approvals/` — 5 files
- `iscc_employee_files/` — 5 files
- `iscc_ess/` — 4 files
- `iscc_gov_integration/` — 4 files
- `iscc_reports/` — 2 files

## Entry points

- `botify_agent/controllers/main.py`

## Most-connected symbols (fan-in leaders)

| Symbol | Kind | Location |
|---|---|---|
| `_error` | function | `botify_agent/controllers/main.py:138` |
| `_json_response` | function | `botify_agent/controllers/main.py:130` |
| `_jsonify` | function | `botify_agent/controllers/main.py:383` |
| `_b64url_encode` | function | `botify_agent/models/botify_security.py:20` |
| `_b64url_decode` | function | `botify_agent/models/botify_security.py:24` |
| `sign_request` | function | `botify_agent/models/botify_security.py:74` |
| `_user_all_groups` | function | `botify_agent/controllers/main.py:97` |
| `_config` | function | `botify_agent/controllers/main.py:111` |
| `BotifyIdentityController` | class | `botify_agent/controllers/main.py:145` |
| `BotifyRpcController` | class | `botify_agent/controllers/main.py:226` |
| `sign_jwt` | function | `botify_agent/models/botify_security.py:29` |
| `verify_jwt` | function | `botify_agent/models/botify_security.py:46` |
| `verify_request` | function | `botify_agent/models/botify_security.py:84` |
| `new_nonce` | function | `botify_agent/models/botify_security.py:104` |
| `ResConfigSettings` | class | `botify_agent/models/res_config_settings.py:7` |
| `TestAssertionSigning` | class | `botify_agent/tests/test_identity.py:17` |
| `TestIdentityController` | class | `botify_agent/tests/test_identity.py:93` |
| `TestEndUserExecution` | class | `botify_agent/tests/test_rpc_permissions.py:24` |
| `TestRequestSigning` | class | `botify_agent/tests/test_rpc_permissions.py:145` |
| `IsccApprovalRoute` | class | `iscc_approvals/models/iscc_approval_route.py:5` |
| `IsccViolation` | class | `iscc_approvals/models/iscc_violation.py:5` |
| `HrAttendance` | class | `iscc_attendance_sync/models/hr_attendance.py:7` |
| `HrEmployee` | class | `iscc_attendance_sync/models/hr_employee.py:5` |
| `ResCompany` | class | `iscc_attendance_sync/models/hr_employee.py:17` |
| `IsccAttendancePunch` | class | `iscc_attendance_sync/models/iscc_attendance_punch.py:9` |
| `IsccAttendanceSource` | class | `iscc_attendance_sync/models/iscc_attendance_source.py:16` |
| `IsccContinuousAbsence` | class | `iscc_continuous_absence/models/iscc_continuous_absence.py:11` |
| `IsccAbsenceScan` | class | `iscc_continuous_absence/wizard/iscc_absence_scan.py:8` |
| `HrEmployee` | class | `iscc_employee_files/models/hr_employee.py:5` |
| `IsccEmployeeDocument` | class | `iscc_employee_files/models/iscc_employee_document.py:7` |

## Highest-importance files

- `botify_agent/controllers/main.py` (400 loc)
- `botify_agent/__init__.py` (3 loc)
- `botify_agent/controllers/__init__.py` (2 loc)
- `botify_agent/models/__init__.py` (3 loc)
- `botify_agent/models/botify_security.py` (106 loc)
- `botify_agent/models/res_config_settings.py` (84 loc)
- `iscc_approvals/__init__.py` (3 loc)
- `iscc_approvals/models/__init__.py` (4 loc)
- `iscc_approvals/models/iscc_approval_route.py` (91 loc)
- `iscc_approvals/models/iscc_violation.py` (55 loc)
- `iscc_attendance_sync/__init__.py` (3 loc)
- `iscc_attendance_sync/__manifest__.py` (38 loc)
- `iscc_attendance_sync/models/__init__.py` (6 loc)
- `iscc_attendance_sync/models/hr_attendance.py` (62 loc)
- `iscc_attendance_sync/models/hr_employee.py` (28 loc)
- `iscc_attendance_sync/models/iscc_attendance_punch.py` (93 loc)
- `iscc_attendance_sync/models/iscc_attendance_source.py` (185 loc)
- `iscc_continuous_absence/__init__.py` (4 loc)
- `iscc_continuous_absence/__manifest__.py` (42 loc)
- `iscc_continuous_absence/models/__init__.py` (3 loc)
- `iscc_continuous_absence/models/iscc_continuous_absence.py` (346 loc)
- `iscc_continuous_absence/wizard/__init__.py` (3 loc)
- `iscc_continuous_absence/wizard/iscc_absence_scan.py` (46 loc)
- `iscc_employee_files/__init__.py` (3 loc)
- `iscc_employee_files/__manifest__.py` (35 loc)