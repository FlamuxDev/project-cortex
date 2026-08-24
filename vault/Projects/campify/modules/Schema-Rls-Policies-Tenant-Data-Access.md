---
cortex-generated: true
title: schema-rls-policies-tenant-data-access
tags: [module]
---

# schema, RLS policies, tenant data access

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `packages/db`

purpose: migrations, RLS policies, and the `withTenant` boundary around every tenant query.
path_prefixes: packages/db
key_files: packages/db/src/tenant.ts, packages/db/migrations/ (39 numbered pairs + 0014_suppression_backfill_via_domain.mjs code migration), scripts/db.mjs, packages/db/test/*.tenancy.test.ts
entrypoints: getPool(), withTenant(), withoutTenantScopeForPlatformAdmin(); `pnpm db:up|migrate|reset|verify`
responsibilities: transaction-scoped tenant context; schema evolution with mandatory .down.sql; invariant verification (`db:verify` asserts FORCE RLS everywhere, app role lacks BYPASSRLS, down files exist).
invariants: every tenant table has workspace_id + ENABLE/FORCE RLS + policy on `current_setting('app.workspace_id')`; tenant set via `select set_config('app.workspace_id',$1,true)` (SET LOCAL takes no binds — interpolation would be injection); unset tenant ERRORS (fail closed, never default); every FK into a tenant table composite on (workspace_id,id) (ADR-0010); migrations immutable once committed.
pitfalls: superuser bypasses RLS even with FORCE; `ON DELETE CASCADE`/FK checks run with RLS disabled — single-column FKs were a real cross-tenant write hole (commit 1e7ead5); concurrent queries on one TenantClient are deprecated by pg — keep sequential (apps/api/src/app.ts:930).
confidence: verified

