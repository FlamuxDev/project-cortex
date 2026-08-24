---
cortex-generated: true
title: audiences-rule-language
tags: [module]
---

# audiences & rule language

**Project:** [[cvm]] | **Confidence:** verified | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/segments/`

purpose: one versioned JSON rule AST (ADR-012) validated against closed per-tenant field catalogue, compiled to parameterised SQL; preview estimate, materialisation, schedules, explain-one-customer walking same AST, exclusions.
path_prefixes: packages/modules/src/segments/
key_files: application/catalogue.ts, segments.ts, preview.ts, materialize.ts, explain.ts, exclusions.ts; domain/; infrastructure/
entrypoints: segmentRoutes (/v1/segments*, /v1/segment-fields)
responsibilities: prefer feature read-model over event scan when compiling; reproducible re-materialisation writes nothing.
invariants: nothing user-written becomes SQL string — keys/values bound as parameters; rule naming `city; drop table customer--` refused at catalogue (security review).
pitfalls: recursive AST needed named schemas in OpenAPI (jsonSchemaTransformObject) or generated types failed.
confidence: verified

## Files (13+)

- `packages/modules/src/segments/application/catalogue.ts`
- `packages/modules/src/segments/application/exclusions.ts`
- `packages/modules/src/segments/application/explain.ts`
- `packages/modules/src/segments/application/materialize.ts`
- `packages/modules/src/segments/application/preview.ts`
- `packages/modules/src/segments/application/segments.ts`
- `packages/modules/src/segments/domain/ast.ts`
- `packages/modules/src/segments/domain/explain.ts`
- `packages/modules/src/segments/domain/validate.ts`
- `packages/modules/src/segments/http/routes.ts`
- `packages/modules/src/segments/index.ts`
- `packages/modules/src/segments/infrastructure/compile.ts`
- `packages/modules/src/segments/jobs.ts`

## API surface

- `POST /exclusion-lists/:code/members`
- `GET /exclusion-lists/:code/members`
- `POST /exclusion-lists`
- `GET /exclusion-lists`
- `PUT /segments/:key/schedule`
- `GET /segments/:key/explain`
- `GET /segments/:key/runs`
- `GET /segments/:key/members`
- `POST /segments/:key/materialize`
- `POST /segments/:key/preview`
- `GET /segments/:key/diff`
- `POST /segments/:key/archive`
- `POST /segments/:key/publish`
- `POST /segments/:key/versions`
- `GET /segments/:key/versions`
