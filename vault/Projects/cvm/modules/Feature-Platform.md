---
cortex-generated: true
title: feature-platform
tags: [module]
---

# feature platform

**Project:** [[cvm]] | **Confidence:** strongly_inferred | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/features/`

purpose: declarative feature definitions compiled to SQL (definitions ARE data — ADR-017), versioned; freshness, lineage; read model customer_feature_current split from record feature_value.
path_prefixes: packages/modules/src/features/
key_files: application/, infrastructure/ (compiler), http/routes.ts, jobs.ts
entrypoints: featureRoutes (/v1/feature-definitions*)
responsibilities: every value records definition version + computed-at; never-computed reads as absent, never 0; changing computation creates new version.
invariants: same compiler used by training extraction and serving (kills train/serve skew at source).
pitfalls: highest-scoring customer labelled `low` bucket bug (594c702).
confidence: strongly_inferred

## Files (11+)

- `packages/modules/src/features/application/compute.ts`
- `packages/modules/src/features/application/current.ts`
- `packages/modules/src/features/application/definitions.ts`
- `packages/modules/src/features/application/refresh.ts`
- `packages/modules/src/features/application/scores.ts`
- `packages/modules/src/features/domain/compile.ts`
- `packages/modules/src/features/domain/defaults.ts`
- `packages/modules/src/features/domain/spec.ts`
- `packages/modules/src/features/http/routes.ts`
- `packages/modules/src/features/index.ts`
- `packages/modules/src/features/jobs.ts`

## API surface

- `POST /feature-definitions/:key/recompute`
- `PATCH /feature-definitions/:key`
- `POST /feature-definitions`
- `GET /feature-definitions/:key`
- `GET /feature-definitions/freshness`
- `GET /feature-definitions`
