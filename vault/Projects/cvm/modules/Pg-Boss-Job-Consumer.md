---
cortex-generated: true
title: pg-boss-job-consumer
tags: [module]
---

# pg-boss job consumer

**Project:** [[cvm]] | **Confidence:** verified | **verified@** `2d7ffcee167d`
**Owns:** `apps/worker/`

purpose: execute all background work; never serves requests.
path_prefixes: apps/worker/
key_files: apps/worker/src/main.ts
entrypoints: `pnpm dev:worker`
responsibilities: import side-effect-registers every module's jobs; subscribeToOutbox('identity.changed') reprojects merge/unmerge parties; startRealtimeDispatch for triggers (optional, degrades to batch); graceful SIGTERM within 30s so non-idempotent sends don't double.
invariants: job handlers finish before exit (retry-after-kill would mean doing work twice, P6 = sending twice).
pitfalls: a dev worker left running during `pnpm test` steals batch leases and makes tests no-op (release record known-limitation 14).
confidence: verified

## Files (1+)

- `apps/worker/src/main.ts`
