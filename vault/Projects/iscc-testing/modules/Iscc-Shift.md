---
cortex-generated: true
title: iscc-shift
tags: [module]
---

# iscc_shift

**Project:** [[iscc-testing]] | **Confidence:** inferred | **verified@** `96dc8874d12b`
**Owns:** `iscc_shift/`

purpose: Shift A/B/C definitions, admin assignment history, overnight shift-date attribution, and the attendance-violation detector.
path_prefixes: iscc_shift/
key_files: models/hr_attendance.py (ATTENDANCE_VIOLATION_CODES = LATE, EARLY_LEAVE, MISSING_OUT, MIN_HOURS), models/iscc_violation.py (adds source-attendance link), data/violation_type_data.xml
entrypoints: inherits `iscc.violation`; evaluated around attendance writes/crons
responsibilities: breach evaluation against assigned shift windows; keeps violations linked to the generating `hr.attendance` row so corrections can re-sync them.
invariants: every attendance-driven violation records `iscc_source_attendance_id` (field help text states this purpose).
pitfalls: README still names a separate module `iscc_attendance_violations` (R17); that directory was deleted and its logic now lives here — documentation drift.
confidence: high

## Files (8+)

- `iscc_shift/__init__.py`
- `iscc_shift/__manifest__.py`
- `iscc_shift/models/__init__.py`
- `iscc_shift/models/hr_attendance.py`
- `iscc_shift/models/hr_employee.py`
- `iscc_shift/models/iscc_continuous_absence.py`
- `iscc_shift/models/iscc_shift.py`
- `iscc_shift/models/iscc_violation.py`
