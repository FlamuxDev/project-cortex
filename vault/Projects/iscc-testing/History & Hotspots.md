---
cortex-generated: true
title: iscc-testing history
tags: [history/project]
---

# iscc-Testing — History & Hotspots

44 mined commits.

## Commit mix

| Category | Count |
|---|---|
| chore | 38 |
| fix | 6 |

## Hotspots (most-changed files — treat changes here carefully)

- `iscc_hr_base/__manifest__.py` — touched 8×
- `iscc_leave_ext/__manifest__.py` — touched 8×
- `iscc_payroll_ext/__manifest__.py` — touched 8×
- `iscc_approvals/__manifest__.py` — touched 7×
- `iscc_hr_base/models/hr_employee.py` — touched 7×
- `iscc_hr_base/models/res_company.py` — touched 7×
- `iscc_payroll_ext/models/iscc_deduction_statement.py` — touched 7×
- `iscc_violations/__manifest__.py` — touched 7×
- `iscc_violations/models/iscc_violation.py` — touched 7×
- `iscc_ess/__manifest__.py` — touched 6×
- `iscc_ess/controllers/portal.py` — touched 6×
- `iscc_hr_base/models/res_config_settings.py` — touched 6×
- `iscc_hr_base/views/res_config_settings_views.xml` — touched 6×
- `iscc_leave_ext/models/hr_leave.py` — touched 6×
- `iscc_shifts/__manifest__.py` — touched 6×
- `iscc_violations/data/mail_template_data.xml` — touched 6×
- `iscc_violations/data/sample_regulation_data.xml` — touched 6×
- `iscc_violations/models/iscc_violation_objection.py` — touched 6×
- `botify_agent/static/src/js/botify_widget.js` — touched 5×
- `iscc_approvals/models/iscc_approval_route.py` — touched 5×

## Recent fixes (past pitfalls live here)

- `96dc8874d1` 2026-08-05 fix: pass identity token directly and avoid race condition in botify widget mounting
- `2012eba7b4` 2026-08-04 Fix identity assertion crash on Odoo 19: res.users.groups_id was removed
- `c77cb223c6` 2026-08-04 Fix double-mount race in the floating widget
- `4ef751ad2d` 2026-08-03 Fix Botify Assistant crash on Odoo 19: use rpc() instead of removed service.
- `c76fcc3775` 2026-07-30 Fix Odoo.sh shift warnings and Odoo 19 leave approval hook.
- `ee07f4841e` 2026-07-30 Fix leave hooks AccessError that broke Odoo.sh hr_holidays tests.
