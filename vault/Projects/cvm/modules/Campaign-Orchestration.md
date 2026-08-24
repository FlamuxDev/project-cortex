---
cortex-generated: true
title: campaign-orchestration
tags: [module]
---

# campaign orchestration

**Project:** [[cvm]] | **Confidence:** verified | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/campaigns/`

purpose: campaigns with fourteen §12 fields, immutable versions, ten pre-launch checks, separation-of-duties approval (409 on launch without; self-approval refused), frozen audience snapshots, targets, runs, funnel snapshots, kill switch with documented halt bound, attribution windows/method-on-every-number.
path_prefixes: packages/modules/src/campaigns/
key_files: application/, domain/, http/routes.ts, jobs.ts
entrypoints: campaignRoutes (/v1/campaigns*, /v1/runs/{id}, /v1/campaign-states)
responsibilities: create→validate→approve→execute loop; typed confirmation for accidental-launch scenario; funnel reconciles against raw tables via callable endpoint.
invariants: delivery state machine belongs to `delivery` NOT here (putting it here created an import cycle — the layering was pointing at the truth).
confidence: verified

## Files (10+)

- `packages/modules/src/campaigns/application/approval.ts`
- `packages/modules/src/campaigns/application/campaigns.ts`
- `packages/modules/src/campaigns/application/execute.ts`
- `packages/modules/src/campaigns/application/runs.ts`
- `packages/modules/src/campaigns/application/validate.ts`
- `packages/modules/src/campaigns/domain/definition.ts`
- `packages/modules/src/campaigns/domain/lifecycle.ts`
- `packages/modules/src/campaigns/http/routes.ts`
- `packages/modules/src/campaigns/index.ts`
- `packages/modules/src/campaigns/jobs.ts`

## API surface

- `GET /campaign-states`
- `GET /customers/:id/marketing`
- `GET /runs/:id/reconcile`
- `GET /runs/:id/funnel`
- `GET /runs/:id/analysis`
- `GET /runs/:id/progress`
- `GET /campaigns/:code/runs`
- `POST /runs/:id/kill`
- `POST /runs/:id/resume`
- `POST /runs/:id/pause`
- `POST /campaigns/:code/launch`
- `POST /campaigns/:code/approval`
- `POST /campaigns/:code/request-approval`
- `POST /campaigns/:code/validate`
- `POST /campaigns/:code/versions`
