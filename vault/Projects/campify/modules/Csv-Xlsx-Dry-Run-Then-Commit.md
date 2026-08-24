---
cortex-generated: true
title: csv-xlsx-dry-run-then-commit
tags: [module]
---

# CSV/XLSX dry-run then commit

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `packages/core/src/imports`

purpose: two-phase import: parse/validate/dedupe into a persisted plan, preview it, then apply.
path_prefixes: packages/core/src/imports
key_files: packages/core/src/imports/sheet.ts, dryRun.ts, commit.ts
entrypoints: POST …/imports/preview, PUT …/imports/:jobId/mapping, POST …/imports/:jobId/commit
responsibilities: mapping suggestion + remap; row-level reject reasons; counts derived from stored rows so endpoints can't disagree (apps/api/src/app.ts:1063).
invariants: preview touches zero contacts; commit applies the previewed plan only; per-entry inflation caps and bounded columns (zip-bomb defenses, commits 063c501, fb73083).
pitfalls: 20 MB bodies parsed on the event loop — guarded pre-read + throttled (apps/api/src/app.ts:353); quadratic XLSX parsing was a real outage-class bug.
confidence: verified

