---
cortex-generated: true
title: schema-client-ssot
tags: [module]
---

# Schema + client SSOT

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `packages/core/src/db/`

purpose: Drizzle schema (36 tables) + pooled postgres client.
path_prefixes: packages/core/src/db/
key_files: schema.ts, index.ts (DbClient/DbOrTx)
entrypoints: drizzle.config.ts points here (`pnpm db:*`)
responsibilities: table definitions, types ($inferSelect), transaction handle type
invariants: any column added here must also get an idempotent SQL file in scripts/ + ORDER entry in server-up.sh
pitfalls: dev uses `db:push`; prod uses hand-written SQL — schema.ts alone does NOT migrate prod
confidence: high

## Files (2+)

- `packages/core/src/db/index.ts`
- `packages/core/src/db/schema.ts`
