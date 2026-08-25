---
cortex-generated: true
title: ast-compiled-to-parameterised-sql
tags: [module]
---

# AST compiled to parameterised SQL

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `packages/core/src/segments`

purpose: dynamic/static audiences defined as JSON AST, compiled live with bind params only.
path_prefixes: packages/core/src/segments
key_files: packages/core/src/segments/ast.ts, compile.ts, repository.ts
entrypoints: POST …/segments(/preview|/:id/recount|/:id/snapshot); used by campaign audience + snapshot freeze
responsibilities: validate AST against closed field allow-list; live count/sample; static snapshots freeze member ids at launch (campaign approval, repeatable-read tx).
invariants: NO value from the definition is ever concatenated into SQL — hostile-input unit tested (compile.ts header); SQL is never persisted.
pitfalls: pathological definitions (199 `not_contains` leaves) ran 56s — statement_timeout (migration 0011) + per-route throttle cap the class (apps/api/src/app.ts:1207).
confidence: verified

## Files (4+)

- `packages/core/src/segments/ast.ts`
- `packages/core/src/segments/compile.ts`
- `packages/core/src/segments/compile.unit.test.ts`
- `packages/core/src/segments/repository.ts`
