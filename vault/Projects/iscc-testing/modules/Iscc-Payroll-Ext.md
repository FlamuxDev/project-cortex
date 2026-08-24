---
cortex-generated: true
title: iscc-payroll-ext
tags: [module]
---

# iscc_payroll_ext

**Project:** [[iscc-testing]] | **Confidence:** inferred | **verified@** `96dc8874d12b`
**Owns:** `iscc_payroll_ext/`

purpose: Monthly deduction statements with a cap and carry-over between months, posted onto Enterprise payslips.
path_prefixes: iscc_payroll_ext/
key_files: models/iscc_deduction_statement.py (`generate_for_period`, `_prev_carry`, `action_confirm/action_post`, `_iscc_propagate_carryover`, `_iscc_refresh_period_payslip`), wizard/iscc_deduction_generate.py, data/hr_payslip_input_type_data.xml
entrypoints: statement workflow + generation wizard
responsibilities: aggregate confirmed violations per employee/period, cap enforcement, carry remaining balance forward, feed DEDUCTION payslip input (the data record enables `available_in_attachments=True` without which Odoo never creates the input — comment cites R11 posting).
invariants: depends on Enterprise `hr_payroll` (README says skip on Community).
pitfalls: carry-over propagation order across periods; reset-to-draft path re-refreshes payslips.
confidence: medium-high

## Files (6+)

- `iscc_payroll_ext/__init__.py`
- `iscc_payroll_ext/__manifest__.py`
- `iscc_payroll_ext/models/__init__.py`
- `iscc_payroll_ext/models/iscc_deduction_statement.py`
- `iscc_payroll_ext/wizard/__init__.py`
- `iscc_payroll_ext/wizard/iscc_deduction_generate.py`
