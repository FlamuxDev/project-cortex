---
cortex-generated: true
title: outbox-relay-housekeeping
tags: [module]
---

# outbox relay & housekeeping

**Project:** [[cvm]] | **Confidence:** strongly_inferred | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/maintenance/`

purpose: outbox_message relay to subscribers (outbox.relay cron), retention enforcement, partition creation via SECURITY DEFINER, dashboard metrics.
path_prefixes: packages/modules/src/maintenance/
key_files: maintenance/index.ts, MAINTENANCE_SCHEDULE
confidence: strongly_inferred

## Files (2+)

- `packages/modules/src/maintenance/index.ts`
- `packages/modules/src/maintenance/jobs.ts`
