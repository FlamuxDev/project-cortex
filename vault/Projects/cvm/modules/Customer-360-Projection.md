---
cortex-generated: true
title: customer-360-projection
tags: [module]
---

# Customer 360 projection

**Project:** [[cvm]] | **Confidence:** verified | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/profile/`

purpose: materialised per-customer profile (not a view), timeline, PII masking, gated+audited export.
path_prefixes: packages/modules/src/profile/
key_files: application/project.ts (idempotent projector writing nothing when unchanged), read.ts, masking.ts, export.ts; jobs.ts
entrypoints: profileRoutes (/v1/customers/{id} cluster, 13 operations incl. export)
responsibilities: rebuild from identity graph on identity.changed; projection state tracked in profile_projection_state.
invariants: projector idempotent; export audited; masked fields by permission.
pitfalls: category-filter 500-then-nothing bug (55d8c35); "a file load about somebody is not that person doing something" timeline semantics fix (802f6c5).
confidence: verified

## Files (7+)

- `packages/modules/src/profile/application/export.ts`
- `packages/modules/src/profile/application/masking.ts`
- `packages/modules/src/profile/application/project.ts`
- `packages/modules/src/profile/application/read.ts`
- `packages/modules/src/profile/http/routes.ts`
- `packages/modules/src/profile/index.ts`
- `packages/modules/src/profile/jobs.ts`

## API surface

- `POST /customers/export`
- `POST /customers/:id/reproject`
- `GET /customers/:id/identity`
- `GET /customers/:id/features`
- `GET /customers/:id/timeline`
- `GET /customers/:id`
- `GET /customers`
