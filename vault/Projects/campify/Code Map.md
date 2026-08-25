---
cortex-generated: true
title: campify code map
tags: [codemap/project]
---

# Campify — Code Map

## Directory layout (indexed files)

- `packages/` — 196 files
- `apps/` — 92 files
- `scripts/` — 6 files
- `e2e/` — 1 files
- `eslint.config.js/` — 1 files
- `playwright.config.ts/` — 1 files
- `vitest.workspace.ts/` — 1 files

## Entry points

- `apps/api/src/app.ts`
- `apps/web/src/app/api/signup/route.ts`
- `apps/web/src/app/(app)/app/team/page.tsx`
- `apps/web/src/app/(app)/app/plan/page.tsx`
- `apps/web/src/app/api/login/route.ts`
- `apps/web/src/app/api/campaigns/[id]/report.csv/route.ts`
- `apps/web/src/app/(public)/invitation/page.tsx`
- `packages/adapters/email-resend/src/index.ts`
- `packages/adapters/fake/src/index.ts`
- `packages/adapters/queue-inprocess/src/index.ts`
- `packages/db/src/index.ts`
- `apps/web/src/app/(app)/app/analytics/page.tsx`
- `apps/web/src/app/(app)/app/campaigns/[id]/report/page.tsx`
- `apps/web/src/app/(app)/app/contacts/import/page.tsx`
- `apps/web/src/app/(app)/app/crm/deals/[id]/page.tsx`

## Most-connected symbols (fan-in leaders)

| Symbol | Kind | Location |
|---|---|---|
| `t` | function | `apps/web/src/lib/i18n.ts:1382` |
| `t` | function | `apps/web/src/components/SegmentBuilder.tsx:163` |
| `withTenant` | function | `packages/db/src/tenant.ts:56` |
| `createContact` | function | `packages/core/src/contacts/repository.ts:64` |
| `messages` | sql_table | `packages/db/migrations/0021_delivery.sql:30` |
| `recordAudit` | function | `packages/core/src/audit/index.ts:125` |
| `email` | function | `apps/api/test/analyticsRoutes.contract.test.ts:31` |
| `email` | function | `apps/api/test/api.contract.test.ts:22` |
| `email` | function | `apps/api/test/apiReadRoutes.contract.test.ts:22` |
| `email` | function | `apps/api/test/authz.contract.test.ts:34` |
| `email` | function | `apps/api/test/campaigns.contract.test.ts:32` |
| `email` | function | `apps/api/test/crmRoutes.contract.test.ts:22` |
| `email` | function | `apps/api/test/deliveryRoutes.contract.test.ts:32` |
| `email` | function | `apps/api/test/journeyRoutes.contract.test.ts:22` |
| `email` | function | `apps/api/test/salesTaskRoutes.contract.test.ts:22` |
| `email` | function | `apps/api/test/webhookRoutes.contract.test.ts:23` |
| `email` | function | `apps/worker/test/analyticsPipeline.integration.test.ts:52` |
| `email` | function | `apps/worker/test/journeyPipeline.integration.test.ts:45` |
| `email` | function | `apps/worker/test/pipeline.integration.test.ts:61` |
| `email` | function | `apps/worker/test/webhookPipeline.integration.test.ts:38` |
| `can` | function | `packages/core/src/identity/rbac.ts:154` |
| `email` | function | `packages/core/test/analytics.integration.test.ts:49` |
| `email` | function | `packages/core/test/approval.integration.test.ts:59` |
| `email` | function | `packages/core/test/campaigns.integration.test.ts:49` |
| `email` | function | `packages/core/test/crm.integration.test.ts:37` |
| `email` | function | `packages/core/test/delivery.integration.test.ts:45` |
| `email` | function | `packages/core/test/domain.integration.test.ts:56` |
| `email` | function | `packages/core/test/journeys.integration.test.ts:47` |
| `email` | function | `packages/core/test/plans.integration.test.ts:54` |
| `email` | function | `packages/core/test/sales.integration.test.ts:38` |

## Highest-importance files

- `apps/api/src/app.ts` (1461 loc)
- `apps/web/src/app/api/signup/route.ts` (117 loc)
- `apps/web/src/app/(app)/app/team/page.tsx` (259 loc)
- `apps/web/src/app/(app)/app/plan/page.tsx` (134 loc)
- `apps/web/src/app/api/login/route.ts` (167 loc)
- `apps/api/src/deliveryRoutes.ts` (231 loc)
- `apps/web/src/app/api/campaigns/[id]/report.csv/route.ts` (45 loc)
- `apps/web/src/lib/actions.ts` (1111 loc)
- `apps/web/src/app/(public)/invitation/page.tsx` (92 loc)
- `apps/api/src/campaignRoutes.ts` (1196 loc)
- `apps/web/src/lib/api.ts` (163 loc)
- `packages/adapters/email-resend/src/index.ts` (194 loc)
- `packages/adapters/fake/src/index.ts` (198 loc)
- `packages/adapters/queue-inprocess/src/index.ts` (242 loc)
- `packages/db/src/index.ts` (24 loc)
- `apps/web/src/app/(app)/app/analytics/page.tsx` (130 loc)
- `apps/web/src/app/(app)/app/campaigns/[id]/report/page.tsx` (233 loc)
- `apps/web/src/app/(app)/app/contacts/import/page.tsx` (62 loc)
- `apps/web/src/app/(app)/app/crm/deals/[id]/page.tsx` (176 loc)
- `apps/web/src/app/(app)/app/crm/page.tsx` (156 loc)
- `apps/web/src/app/(app)/app/journeys/[id]/page.tsx` (125 loc)
- `apps/web/src/app/(app)/app/journeys/page.tsx` (85 loc)
- `apps/web/src/app/(app)/app/sales-tasks/page.tsx` (147 loc)
- `apps/web/src/app/(app)/app/segments/page.tsx` (204 loc)
- `apps/web/src/app/(public)/signup/page.tsx` (99 loc)