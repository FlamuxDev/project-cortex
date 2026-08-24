---
cortex-generated: true
title: iscc-continuous-absence
tags: [module]
---

# iscc_continuous_absence

**Project:** [[iscc-testing]] | **Confidence:** inferred | **verified@** `96dc8874d12b`
**Owns:** `iscc_continuous_absence/`

purpose: Daily detection of employees with no punches for N days; auto-issue absence violation + report.
path_prefixes: iscc_continuous_absence/
key_files: models/iscc_continuous_absence.py, wizard/iscc_absence_scan.py, data/ir_cron_data.xml
entrypoints: daily cron `model._cron_detect_continuous_absence()`; manual scan wizard
responsibilities: scan, sequence-numbered case creation, report views.
confidence: medium-high

## Files (6+)

- `iscc_continuous_absence/__init__.py`
- `iscc_continuous_absence/__manifest__.py`
- `iscc_continuous_absence/models/__init__.py`
- `iscc_continuous_absence/models/iscc_continuous_absence.py`
- `iscc_continuous_absence/wizard/__init__.py`
- `iscc_continuous_absence/wizard/iscc_absence_scan.py`
