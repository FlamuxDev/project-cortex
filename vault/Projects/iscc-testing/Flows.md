---
cortex-generated: true
title: iscc-testing flows
tags: [flows/project]
---

# iscc-Testing — Product Flows

End-to-end behaviors as verified from source. Files are the evidence trail.

## violation-to-paypayslip
**Trigger:** any detector (shift breaches, continuous absence) or manual issue
*[[iscc-testing]] · confidence: medium*

trigger: any detector (shift breaches, continuous absence) or manual issue
steps: detector evaluates → `iscc.violation.action_issue()` → notification mail → optional objection/review → confirm → monthly `generate_for_period` aggregates with cap + prior carry-over → confirm/post → DEDUCTION salary attachment becomes payslip input → carry-over propagated to next period.
files: iscc_violations/models/iscc_violation.py, iscc_payroll_ext/models/iscc_deduction_statement.py, iscc_payroll_ext/data/hr_payslip_input_type_data.xml
confidence: medium-high

**Files:**
- `iscc_violations/models/iscc_violation.py`
- `iscc_payroll_ext/models/iscc_deduction_statement.py`
- `iscc_payroll_ext/data/hr_payslip_input_type_data.xml`

## attendance-ingest
**Trigger:** hourly cron (when enabled) or manual sync
*[[iscc-testing]] · confidence: high*

trigger: hourly cron (when enabled) or manual sync
steps: `iscc.attendance.source._cron_sync_attendance` → fetch punches since cursor (`requests.get` or mock) → match employee by external id → create `hr.attendance` (overnight-aware) → shift detector may issue violations linked to source attendance.
files: iscc_attendance_sync/models/*.py, iscc_shift/models/hr_attendance.py
confidence: high

**Files:**
- `iscc_attendance_sync/models/*.py`
- `iscc_shift/models/hr_attendance.py`

## botify-chat-as-user
**Trigger:** employee clicks floating widget
*[[iscc-testing]] · confidence: high*

trigger: employee clicks floating widget
steps: client action calls `/botify_agent/identity` (server reads `request.env.user`, signs assertion) → browser relays to Botify → Botify verifies signature/jti/expiry → later Botify POSTs `/botify_agent/rpc` with HMAC naming uid → Odoo executes allowlisted method under `with_user(uid)`.
files: botify_agent/controllers/main.py, botify_agent/static/src/js/botify_widget.js
confidence: high

**Files:**
- `botify_agent/controllers/main.py`
- `botify_agent/static/src/js/botify_widget.js`
