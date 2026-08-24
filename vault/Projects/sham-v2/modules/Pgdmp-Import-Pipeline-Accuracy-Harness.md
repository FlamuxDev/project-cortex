---
cortex-generated: true
title: pgdmp-import-pipeline-accuracy-harness
tags: [module]
---

# PGDMP import pipeline & accuracy harness

**Project:** [[sham-v2]] | **Confidence:** inferred | **verified@** `71fbe7ede70c`
**Owns:** `src/sync/,test/eval/`

purpose: rebuild catalogs from S3-fetched backups nightly; measure answer correctness continuously.
path_prefixes: src/sync/, test/eval/
key_files: sync/pg-backup.js, sync/import-backup.js, sync/scheduler.js (node-cron; commit 3650fed closed the last manual data path); test/eval/run.js + cases-schema.js (488 cases GENERATED from the schema map itself — coverage grows with new columns) + cases-natural.js (105 handwritten dialect cases incl. expected refusals); ground truth computed by executing reference queries on the same file, compared on ROWS not prose (README.md:94-113)
entrypoints: `npm run eval [-- --suite|--id]`, failures land in test/eval/failures.json
responsibilities: regression gate — "any new eval failure is a regression; fix it or explain the expectation change in the same commit" (AGENTS.md)
confidence: high

## Files (8+)

- `src/sync/import-backup.js`
- `src/sync/pg-backup.js`
- `src/sync/pg-schema.js`
- `src/sync/scheduler.js`
- `src/sync/teacher-record.js`
- `test/eval/cases-natural.js`
- `test/eval/cases-schema.js`
- `test/eval/run.js`

## API surface

- `GET posts`
- `GET users`
- `GET institutions`
- `GET teacher_districts`
- `GET governorates`
- `GET cities`
- `GET districts`
- `GET teacher_grade_levels`
- `GET teacher_specializations`
- `GET teacher_more_info`
- `GET grade_levels`
- `GET specializations`
- `GET user_reviews`
- `GET university_majors`
- `GET institution_details`
