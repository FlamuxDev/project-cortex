---
cortex-generated: true
title: follow-up-queue
tags: [module]
---

# follow-up queue

**Project:** [[campify]] | **Confidence:** strongly_inferred | **verified@** `ad245fa6ef3d`
**Owns:** `packages/core/src/sales`

purpose: tasks handed from campaigns/journeys to humans, assigned, tracked to outcome.
path_prefixes: packages/core/src/sales
key_files: packages/core/src/sales/state.ts, context.ts, repository.ts
entrypoints: /v1/workspaces/:id/sales-tasks* (assign/transition/notes); journey Task node creates them
responsibilities: explicit open→claimed→done/canceled style machine (no reopen row — unrequested); context assembly rolls contact+campaign history for the assignee.
invariants: transitions table-driven like campaigns; dashboard rollup aggregates.
pitfalls: independent-review defect pass was needed even here (commit 24d8656).
confidence: strongly_inferred

## Files (4+)

- `packages/core/src/sales/context.ts`
- `packages/core/src/sales/repository.ts`
- `packages/core/src/sales/state.ts`
- `packages/core/src/sales/state.unit.test.ts`
