---
cortex-generated: true
title: delivery-engine-process
tags: [module]
---

# delivery engine process

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `apps/worker/src`

purpose: all outbound side effects owned here; five polls per 5s tick.
path_prefixes: apps/worker/src
key_files: apps/worker/src/main.ts, container.ts
entrypoints: node apps/worker/dist/main.js
responsibilities: campaign starts, message dispatch, journey entries/steps, webhook deliveries; readiness line printed only after first successful tick; boots declaring REAL vs fake email out loud.
invariants: one campaign/job failure doesn't kill the tick; errors logged message-only (pg constraint detail embeds contact PII).
confidence: verified

## Files (3+)

- `apps/worker/src/container.ts`
- `apps/worker/src/container.unit.test.ts`
- `apps/worker/src/main.ts`
