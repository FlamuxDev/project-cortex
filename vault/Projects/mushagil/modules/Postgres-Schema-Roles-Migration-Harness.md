---
cortex-generated: true
title: postgres-schema-roles-migration-harness
tags: [module]
---

# Postgres Schema, Roles & Migration Harness

**Project:** [[mushagil]] | **Confidence:** verified | **verified@** `638838aad84d`
**Owns:** `packages/database/migrations,packages/database/src`

purpose: authoritative schema (platform + business schemas), DB roles, checksummed forward-only migrations.
path_prefixes: packages/database/migrations, packages/database/src
key_files: migrations/0001_platform_foundation.sql … 0004_business_setup_catalog_capacity.sql (1405 lines, 29 business tables), src/pools.ts (app/identity/relay/admin/test pools), src/migration-runner/{runner,checksum,discover,cli}.ts, src/schema/*.ts (Drizzle mappings)
entrypoints: `pnpm db:migrate|db:status|db:recreate`; runner CLI src/migration-runner/cli.ts
responsibilities: migration checksums + locks; recreate guard test prevents wiping non-local DBs.
invariants: RLS enabled AND forced on every tenant table across APP_SCHEMAS=["platform","business"] except exactly platform.schema_migration and platform.app_user (tests/migrations/rls-invariant.test.ts, generalized per ADR 0003); mushagil_relay grant scope asserted minimal (tests/security/relay-role-least-privilege.test.ts).
pitfalls: history is never rewritten — M01's deferred tenant FKs were closed later via NOT VALID + VALIDATE (0003, M02 evidence "fk debt"); new schema ⇒ must deliberately add to APP_SCHEMAS or its tables silently escape the invariant.
confidence: verified

