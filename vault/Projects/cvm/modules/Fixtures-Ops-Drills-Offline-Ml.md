---
cortex-generated: true
title: fixtures-ops-drills-offline-ml
tags: [module]
---

# fixtures, ops drills, offline ML

**Project:** [[cvm]] | **Confidence:** verified | **verified@** `2d7ffcee167d`
**Owns:** `tools/,ml/`

purpose: datagen (deliberately dirty synthetic telco dataset — 53k customers/3.38M events fixture), seed (dev tenant+admins), provision (end-to-end tenant provisioning), gameday (12 failure scenarios) + restore drill, loadtest (ingest ack, c360 read, segment materialise, decision latency, ui worst-screen, k6 js), i18n check/sweep, db/init-roles, wiring/check.ts, ml tools extract→train→register + fixture loader; ml/ Python package cvm_ml (train, evaluate, dataset, card) offline-only.
path_prefixes: tools/, ml/
key_files: tools/wiring/check.ts, tools/datagen/generate.ts, tools/loadtest/ui-apis.ts, ml/src/cvm_ml/train.py
confidence: verified

## Files (40+)

- `ml/src/cvm_ml/__init__.py`
- `ml/src/cvm_ml/__main__.py`
- `ml/src/cvm_ml/card.py`
- `ml/src/cvm_ml/dataset.py`
- `ml/src/cvm_ml/evaluate.py`
- `ml/src/cvm_ml/train.py`
- `ml/tests/test_train.py`
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
- `tools/datagen/generate.ts`
- `tools/db/init-roles.ts`
- `tools/gameday/restore-drill.ts`
- `tools/gameday/run.ts`

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
