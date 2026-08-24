---
cortex-generated: true
title: class-level-defect-hunters
tags: [module]
---

# class-level defect hunters

**Project:** [[test-ai]] | **Confidence:** inferred | **verified@** `ec5e16f84200`
**Owns:** `tools/audit_*.py`

purpose: One script per bug family so regressions are caught by category, not by incident report.
path_prefixes: tools/audit_*.py
key_files: audit_enums (declared vocab vs column reality), audit_coverage (unreachable source columns), audit_resolution (every place finds itself), audit_vocab (substring collisions), audit_aliases (dangling synonyms), audit_claims (--fix regenerates claimed numbers from data), audit_filters (execute every field×op combo), audit_views (materialize every cell), audit_robustness (40 garbled questions + 13 adversarial plans), audit_semantics (fields narrower than the questions that attract them), audit_school_filters
confidence: high

