---
cortex-generated: true
title: iscc-violations
tags: [module]
---

# iscc_violations

**Project:** [[iscc-testing]] | **Confidence:** inferred | **verified@** `96dc8874d12b`
**Owns:** `iscc_violations/`

purpose: Single engine for disciplinary violations: types, penalty ladder, objections, cancellation, notifications, warning PDF.
path_prefixes: iscc_violations/
key_files: models/iscc_violation.py, models/iscc_penalty_rule.py, models/iscc_violation_objection.py, wizard/iscc_violation_cancel.py, data/sample_regulation_data.xml, data/mail_template_data.xml
entrypoints: installed via Apps; consumed by all detector modules
responsibilities: state lifecycle (`action_issue/_reset_to_draft/_register_objection/_start_review/_confirm/_cancel/_reverse_from_leave`), prior-occurrence counting to pick the N-th rung of the penalty ladder, deduction computation, employee notification.
invariants: all detectors must issue via `action_issue()` (README architecture rule).
pitfalls: leave reversal interacts with `iscc_leave_ext`; cancellation has two modes (`mode="cancel"` vs reverse) in `_apply_cancellation`.
confidence: high

## Files (9+)

- `iscc_violations/__init__.py`
- `iscc_violations/__manifest__.py`
- `iscc_violations/models/__init__.py`
- `iscc_violations/models/iscc_penalty_rule.py`
- `iscc_violations/models/iscc_violation.py`
- `iscc_violations/models/iscc_violation_objection.py`
- `iscc_violations/models/iscc_violation_type.py`
- `iscc_violations/wizard/__init__.py`
- `iscc_violations/wizard/iscc_violation_cancel.py`
