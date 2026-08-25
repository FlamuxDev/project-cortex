---
cortex-generated: true
title: mythos db
tags: [database/project]
---

# mythos — Database

33 entities.

## table (24)

- **** — `ui-tui/src/__tests__/syntax.test.ts`
- **bash** — `ui-tui/src/__tests__/syntax.test.ts`
- **credit_ledger** — `mythos-cloud/migrations/0003_credits.sql`
- **credit_ledger** — `mythos-cloud/migrations/0100_postgres_schema.sql`
- **device_sessions** — `mythos-cloud/migrations/0001_init.sql`
- **js** — `ui-tui/src/__tests__/syntax.test.ts`
- **models** — `mythos-cloud/migrations/0001_init.sql`
- **models** — `mythos-cloud/migrations/0100_postgres_schema.sql`
- **plan_models** — `mythos-cloud/migrations/0001_init.sql`
- **plan_models** — `mythos-cloud/migrations/0100_postgres_schema.sql`
- **plans** — `mythos-cloud/migrations/0001_init.sql`
- **plans** — `mythos-cloud/migrations/0100_postgres_schema.sql`
- **profiles** — `mythos-cloud/migrations/0001_init.sql`
- **python** — `ui-tui/src/__tests__/syntax.test.ts`
- **rs** — `ui-tui/src/__tests__/syntax.test.ts`
- **sessions** — `mythos-cloud/migrations/0100_postgres_schema.sql`
- **subscriptions** — `mythos-cloud/migrations/0001_init.sql`
- **ts** — `ui-tui/src/__tests__/syntax.test.ts`
- **usage_counters** — `mythos-cloud/migrations/0001_init.sql`
- **usage_counters** — `mythos-cloud/migrations/0100_postgres_schema.sql`
- **usage_events** — `mythos-cloud/migrations/0001_init.sql`
- **usage_events** — `mythos-cloud/migrations/0100_postgres_schema.sql`
- **users** — `mythos-cloud/migrations/0100_postgres_schema.sql`
- **whatever** — `ui-tui/src/__tests__/syntax.test.ts`

## function (9)

- **deduct_credits** — `mythos-cloud/migrations/0003_credits.sql`
- **deduct_credits** — `mythos-cloud/migrations/0100_postgres_schema.sql`
- **grant_credits** — `mythos-cloud/migrations/0003_credits.sql`
- **grant_credits** — `mythos-cloud/migrations/0100_postgres_schema.sql`
- **increment_usage_counter** — `mythos-cloud/migrations/0100_postgres_schema.sql`
- **quota_status** — `mythos-cloud/migrations/0001_init.sql`
- **quota_status** — `mythos-cloud/migrations/0100_postgres_schema.sql`
- **release_reservation** — `mythos-cloud/migrations/0100_postgres_schema.sql`
- **reserve_credits** — `mythos-cloud/migrations/0100_postgres_schema.sql`

## RLS policies (row-level security)

Defense-in-depth check: app-layer tenancy + these policies must BOTH hold.

- `RLS:profiles.own profile` — `mythos-cloud/migrations/0001_init.sql`
- `RLS:device_sessions.own device sessions` — `mythos-cloud/migrations/0001_init.sql`
- `RLS:usage_events.own usage events` — `mythos-cloud/migrations/0001_init.sql`
- `RLS:usage_counters.own usage counters` — `mythos-cloud/migrations/0001_init.sql`
- `RLS:subscriptions.own subscription` — `mythos-cloud/migrations/0001_init.sql`
- `RLS:plans.catalog plans read` — `mythos-cloud/migrations/0001_init.sql`
- `RLS:models.catalog models read` — `mythos-cloud/migrations/0001_init.sql`
- `RLS:plan_models.catalog pm read` — `mythos-cloud/migrations/0001_init.sql`
- `RLS:credit_ledger.own credit ledger` — `mythos-cloud/migrations/0003_credits.sql`
