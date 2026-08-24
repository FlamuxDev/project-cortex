---
cortex-generated: true
title: iscc-leave-ext
tags: [module]
---

# iscc_leave_ext

**Project:** [[iscc-testing]] | **Confidence:** inferred | **verified@** `96dc8874d12b`
**Owns:** `iscc_leave_ext/`

purpose: Reverse pending violations when a leave is approved; convert permissions into leave balance.
path_prefixes: iscc_leave_ext/
key_files: models/hr_leave.py, models/hr_leave_type.py, models/iscc_violation_type.py, data/hr_leave_type_data.xml
entrypoints: hooks into `hr.leave` approval flow
responsibilities: on approval call `action_reverse_from_leave`; provide leave-type data.
pitfalls: history shows the hook caused AccessError inside Odoo.sh's hr_holidays tests (commit ee07f48) and needed an Odoo-19-specific fix (c76fcc3).
confidence: medium-high

## Files (6+)

- `iscc_leave_ext/__init__.py`
- `iscc_leave_ext/__manifest__.py`
- `iscc_leave_ext/models/__init__.py`
- `iscc_leave_ext/models/hr_leave.py`
- `iscc_leave_ext/models/hr_leave_type.py`
- `iscc_leave_ext/models/iscc_violation_type.py`
