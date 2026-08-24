---
cortex-generated: true
title: model-registry-scoring-platform-side-of-track-b
tags: [module]
---

# model registry & scoring (platform side of Track B)

**Project:** [[cvm]] | **Confidence:** verified | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/ml/`

purpose: governed model objects (ADR-009): model/version/deployment/metric/drift_check/challenger/shadow_score/retrain_policy — six-ish tenant-scoped RLS tables audited like offers; deployment requires second-person approval; undeployed version cannot write scores the decision path reads; online inference provider wrapping batch floor; dataset snapshots; customer_score carries model_version_id.
path_prefixes: packages/modules/src/ml/
key_files: ml/index.ts (mlRoutes, onlineScoreProvider, batchScoreProvider), application/, jobs.ts (nightly batch scoring)
entrypoints: mlRoutes (/v1/models*, /v1/models/{code} 13 ops incl /operations, /v1/datasets/{id})
responsibilities: scorer refuses artifact formats it cannot evaluate (sets artifact_uri for tree models instead of guessing); extraction runs platform feature compiler with occurred_at < as_of point-in-time bound.
invariants: train/serve skew checked by test replaying trainer predictions to 1e-9 (packages/modules/__tests__/ml-skew.unit.test.ts).
confidence: verified

## Files (14+)

- `packages/modules/src/ml/application/behaviour.ts`
- `packages/modules/src/ml/application/extract.ts`
- `packages/modules/src/ml/application/governance.ts`
- `packages/modules/src/ml/application/monitor.ts`
- `packages/modules/src/ml/application/online.ts`
- `packages/modules/src/ml/application/registry.ts`
- `packages/modules/src/ml/application/score.ts`
- `packages/modules/src/ml/domain/drift.ts`
- `packages/modules/src/ml/domain/families.ts`
- `packages/modules/src/ml/domain/label.ts`
- `packages/modules/src/ml/domain/model.ts`
- `packages/modules/src/ml/http/routes.ts`
- `packages/modules/src/ml/index.ts`
- `packages/modules/src/ml/jobs.ts`

## API surface

- `GET /models/:code/retrain-policy`
- `PUT /models/:code/retrain-policy`
- `POST /challengers/:id/decision`
- `POST /models/:code/challengers`
- `GET /models/:code/challengers`
- `POST /models/:code/drift`
- `GET /models/:code/drift`
- `GET /customers/:id/scores`
- `GET /models/:code/monitoring`
- `POST /models/:code/score`
- `POST /models/:code/rollback`
- `POST /models/:code/versions/:version/deploy`
- `POST /models/:code/versions/:version/approval`
- `POST /models/:code/versions/:version/request-approval`
- `GET /models/:code/versions/:version`
