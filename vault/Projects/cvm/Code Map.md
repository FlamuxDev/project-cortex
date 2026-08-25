---
cortex-generated: true
title: cvm code map
tags: [codemap/project]
---

# CVM — Code Map

## Directory layout (indexed files)

- `packages/` — 313 files
- `apps/` — 83 files
- `tools/` — 23 files
- `ml/` — 7 files
- `.dependency-cruiser.cjs/` — 1 files
- `deploy/` — 1 files
- `e2e/` — 1 files
- `eslint.config.js/` — 1 files
- `playwright.config.ts/` — 1 files
- `vitest.config.ts/` — 1 files

## Entry points

- `apps/web/src/app/(app)/offers/[code]/page.tsx`
- `apps/web/src/app/(app)/campaigns/[code]/page.tsx`
- `apps/web/src/app/(app)/journeys/[code]/edit/page.tsx`
- `apps/web/src/app/(app)/audiences/[key]/page.tsx`
- `apps/web/src/app/(app)/administration/policy/page.tsx`
- `apps/web/src/app/(app)/integrations/page.tsx`
- `apps/web/src/app/(app)/administration/security/page.tsx`
- `apps/web/src/app/(app)/models/[code]/operations/page.tsx`
- `apps/web/src/app/(app)/models/[code]/page.tsx`
- `apps/web/src/app/(app)/campaigns/page.tsx`
- `apps/web/src/app/(app)/decisions/page.tsx`
- `apps/web/src/app/(app)/journeys/[code]/page.tsx`
- `apps/web/src/app/(app)/offers/page.tsx`
- `apps/web/src/app/(app)/loyalty/[code]/page.tsx`
- `apps/api/src/app.ts`

## Most-connected symbols (fan-in leaders)

| Symbol | Kind | Location |
|---|---|---|
| `x` | function | `apps/web/src/components/journey-builder.tsx:426` |
| `Tenant` | type | `apps/web/src/lib/api.ts:96` |
| `tenant` | sql_table | `packages/platform/src/db/migrations/0001_platform.up.sql:68` |
| `y` | function | `apps/web/src/components/journey-builder.tsx:431` |
| `Text` | function | `apps/web/src/components/journey-builder.tsx:601` |
| `withTenant` | function | `packages/platform/src/db/index.ts:53` |
| `r` | function | `vitest.config.ts:4` |
| `describe` | function | `apps/web/src/components/rule-builder.tsx:143` |
| `describe` | function | `packages/modules/src/segments/infrastructure/compile.ts:684` |
| `describe` | function | `packages/modules/src/analytics/domain/attribution-models.ts:139` |
| `id` | function | `apps/api/__tests__/decisioning.int.test.ts:106` |
| `withCurrentTenant` | function | `packages/platform/src/db/index.ts:181` |
| `audit` | function | `packages/modules/src/identity/application/conflicts.ts:210` |
| `recordAudit` | function | `packages/modules/src/audit/application/record.ts:18` |
| `Table` | function | `apps/web/src/components/ui.tsx:156` |
| `_table` | function | `ml/src/cvm_ml/card.py:22` |
| `context` | function | `apps/api/__tests__/scim.int.test.ts:35` |
| `context` | function | `packages/modules/__tests__/analytics-depth.int.test.ts:30` |
| `context` | function | `packages/modules/__tests__/bandit.int.test.ts:21` |
| `context` | function | `packages/modules/__tests__/behaviour-scores.int.test.ts:22` |
| `context` | function | `packages/modules/__tests__/connector-pull.int.test.ts:47` |
| `context` | function | `packages/modules/__tests__/journeys.int.test.ts:52` |
| `context` | function | `packages/modules/__tests__/loyalty.int.test.ts:50` |
| `Context` | interface | `packages/modules/src/segments/infrastructure/compile.ts:224` |
| `record` | function | `packages/modules/__tests__/connector-pull.int.test.ts:136` |
| `record` | function | `packages/modules/__tests__/decision.unit.test.ts:38` |
| `record` | function | `tools/gameday/run.ts:51` |
| `record` | function | `tools/loadtest/ingest.js:100` |
| `apiOrEmpty` | function | `apps/web/src/lib/api.ts:305` |
| `withSystem` | function | `packages/platform/src/db/index.ts:80` |

## Highest-importance files

- `apps/web/src/app/(app)/offers/[code]/page.tsx` (919 loc)
- `apps/web/src/app/(app)/campaigns/[code]/page.tsx` (1022 loc)
- `apps/web/src/app/(app)/journeys/[code]/edit/page.tsx` (362 loc)
- `apps/web/src/app/(app)/audiences/[key]/page.tsx` (672 loc)
- `packages/modules/src/iam/http/admin-routes.ts` (740 loc)
- `packages/modules/src/loyalty/http/routes.ts` (1004 loc)
- `packages/modules/src/ml/http/routes.ts` (1109 loc)
- `packages/modules/src/campaigns/http/routes.ts` (983 loc)
- `packages/modules/src/segments/http/routes.ts` (1034 loc)
- `packages/modules/src/ingestion/http/routes.ts` (1105 loc)
- `apps/web/src/components/journey-builder.tsx` (885 loc)
- `apps/web/src/lib/i18n.ts` (348 loc)
- `apps/web/src/lib/api.ts` (313 loc)
- `apps/web/src/app/(app)/administration/policy/page.tsx` (577 loc)
- `apps/web/src/app/(app)/integrations/page.tsx` (585 loc)
- `apps/web/src/components/ui.tsx` (937 loc)
- `apps/web/src/app/(app)/administration/security/page.tsx` (546 loc)
- `packages/modules/src/tenancy/http/routes.ts` (435 loc)
- `apps/web/src/app/(app)/models/[code]/operations/page.tsx` (576 loc)
- `apps/web/src/app/(app)/models/[code]/page.tsx` (652 loc)
- `packages/modules/src/catalog/http/routes.ts` (500 loc)
- `packages/modules/src/journeys/http/routes.ts` (521 loc)
- `packages/modules/src/identity/http/routes.ts` (550 loc)
- `packages/modules/src/decision/http/routes.ts` (657 loc)
- `packages/modules/src/privacy/http/routes.ts` (455 loc)