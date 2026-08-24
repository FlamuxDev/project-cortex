---
cortex-generated: true
title: recurring-job-registrar-singleton
tags: [module]
---

# recurring-job registrar (singleton)

**Project:** [[cvm]] | **Confidence:** verified | **verified@** `2d7ffcee167d`
**Owns:** `apps/scheduler/`

purpose: evaluate pg-boss cron and enqueue recurring jobs; enqueues, never executes.
path_prefixes: apps/scheduler/
key_files: apps/scheduler/src/main.ts
entrypoints: `pnpm dev:scheduler`
responsibilities: tryAcquire advisory lock; loser exits cleanly; registers MAINTENANCE/INGESTION/.../EXPERIMENT_SCHEDULE entries.
invariants: singleton enforced by session-scoped Postgres lock, not replica count — rolling updates otherwise run nightly retention N times; lock auto-releases on crash.
pitfalls: missing scheduler looks like a product bug — outbox.relay never fires, merge-reprojection waits 90s (playwright.config.ts comment; CI fixed in ef6ca9a).
confidence: verified

## Files (1+)

- `apps/scheduler/src/main.ts`
