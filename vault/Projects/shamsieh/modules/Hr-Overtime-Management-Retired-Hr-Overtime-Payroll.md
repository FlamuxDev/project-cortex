---
cortex-generated: true
title: hr-overtime-management-retired-hr-overtime-payroll
tags: [module]
---

# hr_overtime_management (+ retired hr_overtime_payroll)

**Project:** [[shamsieh]] | **Confidence:** inferred | **verified@** `ad14342a33e9`
**Owns:** `hr_overtime_management/,hr_overtime_payroll/`

purpose: Overtime requests with multi-level approval and timesheet integration; conversion of approved OT into Time Off (approval-only, no fingerprint banking).
path_prefixes: hr_overtime_management/, hr_overtime_payroll/
key_files: models/, wizard/ (Hourly Departure allocation), report/, tests/test_hr_overtime.py; hr_overtime_payroll/__manifest__.py (uninstall-me stub)
entrypoints: request/approval workflows
responsibilities: OT lifecycle; payroll computation moved out (stub remains for Odoo.sh upgrades).
confidence: medium-high

## Files (40+)

- `hr_overtime_management/__init__.py`
- `hr_overtime_management/__manifest__.py`
- `hr_overtime_management/doc/_check_db.py`
- `hr_overtime_management/doc/_check_employee_access.py`
- `hr_overtime_management/doc/_check_views.py`
- `hr_overtime_management/doc/_check_wage.py`
- `hr_overtime_management/doc/_debug_form_arch.py`
- `hr_overtime_management/doc/_debug_overtime_types.py`
- `hr_overtime_management/doc/_extract_template_style.py`
- `hr_overtime_management/doc/_extract_template_text.py`
- `hr_overtime_management/doc/_finish_repair.py`
- `hr_overtime_management/doc/_fix_company_access_odoo19.py`
- `hr_overtime_management/doc/_fix_company_access_v2_odoo19.py`
- `hr_overtime_management/doc/_fix_corrupted_views_odoo19.py`
- `hr_overtime_management/doc/_fix_employee_access_odoo19.py`
- `hr_overtime_management/doc/_fix_employee_company_field_odoo19.py`
- `hr_overtime_management/doc/_fix_hr_chain_odoo19.py`
- `hr_overtime_management/doc/_fix_overtime_types_odoo19.py`
- `hr_overtime_management/doc/_fix_report_view.py`
- `hr_overtime_management/doc/_fix_views_odoo19.py`
- `hr_overtime_management/doc/_fix_weekend_column_odoo19.py`
- `hr_overtime_management/doc/_migrate_odoo19.py`
- `hr_overtime_management/doc/_recompute_costs.py`
- `hr_overtime_management/doc/_repair_odoo19_schema.py`
- `hr_overtime_management/doc/_repair_overtime_types_odoo19.py`
