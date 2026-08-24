---
cortex-generated: true
title: iscc-hr-base-iscc-approvals-iscc-employee-files-iscc-reports-iscc-gov-integration
tags: [module]
---

# iscc_hr_base / iscc_approvals / iscc_employee_files / iscc_reports / iscc_gov_integration

**Project:** [[iscc-testing]] | **Confidence:** inferred | **verified@** `96dc8874d12b`
**Owns:** `iscc_hr_base/,iscc_approvals/,iscc_employee_files/,iscc_reports/,iscc_gov_integration/`

purpose: Shared foundation (groups/menus/company policy fields), multi-level approval routes wired into the violation model, employee documents with CSV import + record rules + purge cron, analysis-only report menus, and CSV generators for Qiwa/GOSI.
path_prefixes: iscc_hr_base/, iscc_approvals/, iscc_employee_files/, iscc_reports/, iscc_gov_integration/
key_files: iscc_hr_base/models/res_company.py (+res_config_settings, hr_employee); iscc_approvals/models/iscc_approval_route.py; iscc_gov_integration/models/iscc_gov_export.py
entrypoints: gov export `action_generate()` button
responsibilities: base config; approval routing; document governance; reporting menus; government file rows.
invariants: install order matters (README prescribes hr_base → violations → rest).
pitfalls: `_build_rows` is explicitly marked "PLACEHOLDER column mapping — align with the real Qiwa/GOSI template", and the class docstring flags that Qiwa/GOSI have no public write-API, hence CSV + manual upload.
confidence: high (structure), low (gov export content)

## Files (22+)

- `iscc_approvals/__init__.py`
- `iscc_approvals/__manifest__.py`
- `iscc_approvals/models/__init__.py`
- `iscc_approvals/models/iscc_approval_route.py`
- `iscc_approvals/models/iscc_violation.py`
- `iscc_employee_files/__init__.py`
- `iscc_employee_files/__manifest__.py`
- `iscc_employee_files/models/__init__.py`
- `iscc_employee_files/models/hr_employee.py`
- `iscc_employee_files/models/iscc_employee_document.py`
- `iscc_gov_integration/__init__.py`
- `iscc_gov_integration/__manifest__.py`
- `iscc_gov_integration/models/__init__.py`
- `iscc_gov_integration/models/iscc_gov_export.py`
- `iscc_hr_base/__init__.py`
- `iscc_hr_base/__manifest__.py`
- `iscc_hr_base/models/__init__.py`
- `iscc_hr_base/models/hr_employee.py`
- `iscc_hr_base/models/res_company.py`
- `iscc_hr_base/models/res_config_settings.py`
- `iscc_reports/__init__.py`
- `iscc_reports/__manifest__.py`
