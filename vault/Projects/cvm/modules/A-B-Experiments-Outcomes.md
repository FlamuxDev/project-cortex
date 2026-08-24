---
cortex-generated: true
title: a-b-experiments-outcomes
tags: [module]
---

# A/B experiments & outcomes

**Project:** [[cvm]] | **Confidence:** strongly_inferred | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/experiments/`

purpose: deterministic sticky bucketing, control declared first, held-out customers still measured; variants, assignments, sequential stopping, bandit reallocation; conversion attribution inside declared window with method named on every number; uplift NULL without holdout.
path_prefixes: packages/modules/src/experiments/
key_files: application/, http/routes.ts, jobs.ts
entrypoints: experimentRoutes (/v1/experiments*, /reallocate)
confidence: strongly_inferred

## Files (6+)

- `packages/modules/src/experiments/application/bandit.ts`
- `packages/modules/src/experiments/application/experiments.ts`
- `packages/modules/src/experiments/domain/assign.ts`
- `packages/modules/src/experiments/http/routes.ts`
- `packages/modules/src/experiments/index.ts`
- `packages/modules/src/experiments/jobs.ts`

## API surface

- `POST /experiments/reallocate`
- `POST /experiments`
- `GET /experiments/:code`
- `GET /experiments`
