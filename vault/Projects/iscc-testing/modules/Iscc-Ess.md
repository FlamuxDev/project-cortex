---
cortex-generated: true
title: iscc-ess
tags: [module]
---

# iscc_ess

**Project:** [[iscc-testing]] | **Confidence:** inferred | **verified@** `96dc8874d12b`
**Owns:** `iscc_ess/`

purpose: Employee self-service portal pages for violations, details, objection filing.
path_prefixes: iscc_ess/
key_files: controllers/portal.py (extends `CustomerPortal`)
entrypoints: portal routes `/my/...` (`portal_my_violations`, `portal_my_violation_detail`, `portal_file_objection`, `portal_my_objections`)
responsibilities: portal counters, own-record scoping via `_iscc_employee`, objection upload.
invariants: employees see only their own records (commit 99c45d3 restricted the deduction statement likewise).
confidence: high

## Files (4+)

- `iscc_ess/__init__.py`
- `iscc_ess/__manifest__.py`
- `iscc_ess/controllers/__init__.py`
- `iscc_ess/controllers/portal.py`
