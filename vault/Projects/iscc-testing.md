---
cortex-generated: true
title: iscc-testing
tags: [project]
---

# iscc-Testing

**Path:** `/home/aboud/Dev/iscc-Testing`  
**Kind:** app | **Languages:** .py,.js | **Frameworks:** None

**HEAD:** `96dc8874d12b` | **Brain:** `96dc8874d12b` | FRESH

| Files | Symbols | Modules | Flows | APIs | DB | Tests | Decisions | Memories |
|---|---|---|---|---|---|---|---|---|
| 80 | 207 | 9 | 3 | 0 | 0 | 3 | 6 | 17 (0 stale) |

## Modules
- [[iscc-testing/modules/Botify-Agent|botify_agent]] — Floating AI chat widget whose tool calls execute as the logged-in employee, not a shared integration [inferred]
- [[iscc-testing/modules/Iscc-Attendance-Sync|iscc_attendance_sync]] — Pull punches from external systems (Sprinklr or generic HTTP JSON, plus a mock provider) into `hr.at [inferred]
- [[iscc-testing/modules/Iscc-Continuous-Absence|iscc_continuous_absence]] — Daily detection of employees with no punches for N days; auto-issue absence violation + report. [inferred]
- [[iscc-testing/modules/Iscc-Ess|iscc_ess]] — Employee self-service portal pages for violations, details, objection filing. [inferred]
- [[iscc-testing/modules/Iscc-Hr-Base-Iscc-Approvals-Iscc-Employee-Files-Iscc-Reports-Iscc-Gov-Integration|iscc_hr_base / iscc_approvals / iscc_employee_files / iscc_reports / iscc_gov_integration]] — Shared foundation (groups/menus/company policy fields), multi-level approval routes wired into the v [inferred]
- [[iscc-testing/modules/Iscc-Leave-Ext|iscc_leave_ext]] — Reverse pending violations when a leave is approved; convert permissions into leave balance. [inferred]
- [[iscc-testing/modules/Iscc-Payroll-Ext|iscc_payroll_ext]] — Monthly deduction statements with a cap and carry-over between months, posted onto Enterprise paysli [inferred]
- [[iscc-testing/modules/Iscc-Shift|iscc_shift]] — Shift A/B/C definitions, admin assignment history, overnight shift-date attribution, and the attenda [inferred]
- [[iscc-testing/modules/Iscc-Violations|iscc_violations]] — Single engine for disciplinary violations: types, penalty ladder, objections, cancellation, notifica [inferred]

## Flows
- **violation-to-paypayslip** — any detector (shift breaches, continuous absence) or manual issue
- **attendance-ingest** — hourly cron (when enabled) or manual sync
- **botify-chat-as-user** — employee clicks floating widget

## Key knowledge
- Architecture [strongly_inferred]
- Database [strongly_inferred]
- API surface [strongly_inferred]
- Historical lessons [verified]
- iscc-Testing: overview [verified]
- Tests & commands [verified]
