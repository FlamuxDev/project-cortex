---
cortex-generated: true
title: cvm-platform-infrastructure-kernel
tags: [module]
---

# @cvm/platform infrastructure kernel

**Project:** [[cvm]] | **Confidence:** verified | **verified@** `2d7ffcee167d`
**Owns:** `packages/platform/src/`

purpose: ***REDACTED-B64***; imported by everyone, imports NO domain module.
path_prefixes: packages/platform/src/
key_files: db/pool.ts, db/migrate.ts, db/check-rls.ts (6-assertion drift guard), db/schema/index.ts (TENANT_SCOPED_TABLES/PARTITIONED_TABLES/SYSTEM_TABLES registry), http/plugin.ts, http/idempotency.ts, http/ratelimit.ts, http/quota.ts, jobs/index.ts (defineJob/startJobs), jobs/install.ts, storage (ObjectStorePort → S3/MinIO), telemetry/bootstrap.mjs, context/index.ts (ambient request context)
entrypoints: subpath exports package.json#exports (./db, ./http, …)
responsibilities: pool ownership (only platform/db touches pools — dependency-cruiser rule), migrations runner with owner/runtime role split, RLS drift guard, pg-boss lifecycle + install into `pgboss` schema, HTTP pipeline (above), Argon2id crypto, OTel bootstrap.
invariants: runtime DB role has no BYPASSRLS and no DDL; partitions created via SECURITY DEFINER functions; statement timeout configurable.
pitfalls: ESM hoisting defeats startTelemetry() in-process (bootstrap via --import); caught unique violations abort Postgres txns (25P02) — use ON CONFLICT clauses.
confidence: verified

## Files (40+)

- `packages/platform/src/config/dotenv.ts`
- `packages/platform/src/config/index.ts`
- `packages/platform/src/context/index.ts`
- `packages/platform/src/contracts/index.ts`
- `packages/platform/src/crypto/index.ts`
- `packages/platform/src/db/advisory-lock.ts`
- `packages/platform/src/db/check-rls.ts`
- `packages/platform/src/db/errors.ts`
- `packages/platform/src/db/index.ts`
- `packages/platform/src/db/migrate.ts`
- `packages/platform/src/db/migrations/0001_platform.down.sql`
- `packages/platform/src/db/migrations/0001_platform.up.sql`
- `packages/platform/src/db/migrations/0002_self_membership_policy.down.sql`
- `packages/platform/src/db/migrations/0002_self_membership_policy.up.sql`
- `packages/platform/src/db/migrations/0003_nullsafe_rls_policies.down.sql`
- `packages/platform/src/db/migrations/0003_nullsafe_rls_policies.up.sql`
- `packages/platform/src/db/migrations/0004_drop_failed_login_count.down.sql`
- `packages/platform/src/db/migrations/0004_drop_failed_login_count.up.sql`
- `packages/platform/src/db/migrations/0005_data_backbone.down.sql`
- `packages/platform/src/db/migrations/0005_data_backbone.up.sql`
- `packages/platform/src/db/migrations/0006_retention_and_quarantine.down.sql`
- `packages/platform/src/db/migrations/0006_retention_and_quarantine.up.sql`
- `packages/platform/src/db/migrations/0007_partition_race.down.sql`
- `packages/platform/src/db/migrations/0007_partition_race.up.sql`
- `packages/platform/src/db/migrations/0008_customer_360.down.sql`
