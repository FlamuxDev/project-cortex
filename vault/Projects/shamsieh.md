---
cortex-generated: true
title: shamsieh
tags: [project]
---

# shamsieh

**Path:** `/home/aboud/Dev/shamsieh`  
**Kind:** app | **Languages:** .py,.js | **Frameworks:** None

**HEAD:** `ad14342a33e9` | **Brain:** `ad14342a33e9` | FRESH

| Files | Symbols | Modules | Flows | APIs | DB | Tests | Decisions | Memories |
|---|---|---|---|---|---|---|---|---|
| 297 | 1564 | 10 | 4 | 4 | 0 | 23 | 6 | 18 (0 stale) |

## Modules
- [[shamsieh/modules/Botify-Agent-Protocol-V2|Botify Agent (protocol v2)]] — Embed the external Botify AI assistant and let it act strictly as the requesting employee, via grant [inferred]
- [[shamsieh/modules/Crm-Custom-Ext-Project-Custom-Ext-Shams-Todo-Groups|crm_custom_ext / project_custom_ext / shams_todo_groups]] — CRM fields/security/teams/targets/dashboards; project security groups, progress, task templates; Mic [inferred]
- [[shamsieh/modules/Hikvision-Attendance-Service|hikvision_attendance_service]] — Receive Hikvision attendance/access webhooks, persist durably, forward into Odoo. [inferred]
- [[shamsieh/modules/Hr-Attendance-Custom-Extensions|HR Attendance Custom Extensions]] — Attendance core: fingerprint sync (Hikvision + ZKTeco), face attendance enrollment/matching, daily s [inferred]
- [[shamsieh/modules/Hr-Holidays-Custom-Extensions|HR Holidays Custom Extensions]] — Exceptional holidays, leave-balance logic, sick/annual automation, Article 11 hourly departures, rem [inferred]
- [[shamsieh/modules/Hr-Loans-Advances|hr_loans_advances]] — Salary advances and loans with manager/HR approval and repayment handling. [inferred]
- [[shamsieh/modules/Hr-Overtime-Management-Retired-Hr-Overtime-Payroll|hr_overtime_management (+ retired hr_overtime_payroll)]] — Overtime requests with multi-level approval and timesheet integration; conversion of approved OT int [inferred]
- [[shamsieh/modules/Shamsieh-I18N-Ar-Removed-Module-Stubs|shamsieh_i18n_ar + removed-module stubs]] — Professional Arabic translations across apps (generated/maintained via scripts/generate_ar_po.py); u [inferred]
- [[shamsieh/modules/Website-Lead-Api|website_lead_api]] — Public JSON endpoint for external website contact forms to create CRM leads. [inferred]
- [[shamsieh/modules/Zkteco-Attendance-Service|zkteco_attendance_service]] — Poll ZKTeco terminals from a LAN PC and push events into Odoo. [inferred]

## Flows
- **fingerprint-punch-to-attendance** — device event (push) or poller cycle
- **assistant-delegation-v2** — employee opens Botify widget/client action
- **website-lead-ingest** — external site POST `/api/website/lead`
- **wfh-and-overtime-approval** — employee request

## Key knowledge
- Architecture [strongly_inferred]
- Database [strongly_inferred]
- API surface [strongly_inferred]
- Historical lessons [verified]
- shamsieh: overview [verified]
- Tests & commands [verified]
