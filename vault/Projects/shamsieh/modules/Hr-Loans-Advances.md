---
cortex-generated: true
title: hr-loans-advances
tags: [module]
---

# hr_loans_advances

**Project:** [[shamsieh]] | **Confidence:** inferred | **verified@** `ad14342a33e9`
**Owns:** `hr_loans_advances/`

purpose: Salary advances and loans with manager/HR approval and repayment handling.
path_prefixes: hr_loans_advances/
key_files: models/, wizard/
responsibilities: loan request lifecycle; approver resolution without requiring res.company read access (c5ffc75c, e3d32f88 fixed AccessError).
confidence: medium

## Files (17+)

- `hr_loans_advances/__init__.py`
- `hr_loans_advances/__manifest__.py`
- `hr_loans_advances/migrations/19.0.1.0.2/post-migrate.py`
- `hr_loans_advances/models/__init__.py`
- `hr_loans_advances/models/hr_employee_advance.py`
- `hr_loans_advances/models/hr_employee_advance_approval_line.py`
- `hr_loans_advances/models/hr_employee_advance_repayment.py`
- `hr_loans_advances/models/hr_employee_loan.py`
- `hr_loans_advances/models/hr_employee_loan_approval_line.py`
- `hr_loans_advances/models/hr_employee_loan_payment.py`
- `hr_loans_advances/models/hr_loans_advances_mixin.py`
- `hr_loans_advances/tests/__init__.py`
- `hr_loans_advances/tests/test_hr_employee_advance.py`
- `hr_loans_advances/tests/test_hr_employee_loan.py`
- `hr_loans_advances/wizard/__init__.py`
- `hr_loans_advances/wizard/hr_advance_refuse_wizard.py`
- `hr_loans_advances/wizard/hr_loan_refuse_wizard.py`
