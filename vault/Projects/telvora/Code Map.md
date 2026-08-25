---
cortex-generated: true
title: telvora code map
tags: [codemap/project]
---

# Telvora — Code Map

## Directory layout (indexed files)

- `services/` — 410 files
- `apps/` — 262 files
- `e2e/` — 40 files
- `packages/` — 33 files
- `infra/` — 11 files
- `load/` — 2 files

## Entry points

- `apps/web/src/app/api/leads/route.ts`
- `apps/web/src/app/api/tenant/offers/route.ts`
- `apps/web/src/app/api/tenant/approvals/workflows/route.ts`
- `apps/web/src/app/api/tenant/integrations/route.ts`
- `apps/web/src/app/api/tenant/model-studio/runs/route.ts`
- `apps/web/src/app/api/tenant/offers/[id]/versions/route.ts`
- `apps/web/src/app/api/tenant/ai/policy/route.ts`
- `apps/web/src/app/api/tenant/campaigns/route.ts`
- `apps/web/src/app/api/tenant/consent/events/route.ts`
- `apps/web/src/app/api/tenant/consent/policy/route.ts`
- `apps/web/src/app/api/tenant/models/[id]/versions/from-template/route.ts`
- `apps/web/src/app/api/tenant/models/[id]/versions/route.ts`
- `apps/web/src/app/api/tenant/onboarding/route.ts`
- `apps/web/src/app/api/platform-admin/tenants/route.ts`
- `apps/web/src/app/api/tenant/analytics/export/route.ts`

## Most-connected symbols (fan-in leaders)

| Symbol | Kind | Location |
|---|---|---|
| `f` | function | `infra/cdk/cdk.out/asset.02b51ab524e7bcf8f477de3e71e5f9a72e448301b26ba62e9e75a14f9c55a093/index.js:37` |
| `n` | function | `infra/cdk/cdk.out/asset.02b51ab524e7bcf8f477de3e71e5f9a72e448301b26ba62e9e75a14f9c55a093/index.js:11` |
| `S` | component | `infra/cdk/cdk.out/asset.02b51ab524e7bcf8f477de3e71e5f9a72e448301b26ba62e9e75a14f9c55a093/index.js:23` |
| `R` | component | `infra/cdk/cdk.out/asset.02b51ab524e7bcf8f477de3e71e5f9a72e448301b26ba62e9e75a14f9c55a093/index.js:19` |
| `G` | component | `infra/cdk/cdk.out/asset.02b51ab524e7bcf8f477de3e71e5f9a72e448301b26ba62e9e75a14f9c55a093/index.js:8` |
| `c` | function | `infra/cdk/cdk.out/asset.02b51ab524e7bcf8f477de3e71e5f9a72e448301b26ba62e9e75a14f9c55a093/index.js:28` |
| `d` | function | `infra/cdk/cdk.out/asset.02b51ab524e7bcf8f477de3e71e5f9a72e448301b26ba62e9e75a14f9c55a093/index.js:34` |
| `Store` | struct | `services/core-api/internal/alerts/store.go:18` |
| `Store` | struct | `services/core-api/internal/analytics/store.go:23` |
| `Store` | struct | `services/core-api/internal/approvals/store.go:29` |
| `Store` | struct | `services/core-api/internal/audit/store.go:15` |
| `Store` | struct | `services/core-api/internal/auth/store.go:23` |
| `Store` | struct | `services/core-api/internal/campaigns/store.go:28` |
| `Store` | struct | `services/core-api/internal/channels/store.go:15` |
| `Store` | struct | `services/core-api/internal/consent/store.go:21` |
| `Store` | struct | `services/core-api/internal/customer360/store.go:15` |
| `Store` | struct | `services/core-api/internal/dataquality/store.go:18` |
| `Store` | struct | `services/core-api/internal/decisions/store.go:20` |
| `Store` | struct | `services/core-api/internal/dsar/store.go:24` |
| `Store` | struct | `services/core-api/internal/executive/model.go:92` |
| `Store` | struct | `services/core-api/internal/experiments/store.go:25` |
| `Store` | struct | `services/core-api/internal/features/store.go:15` |
| `Store` | struct | `services/core-api/internal/identity/store.go:21` |
| `Store` | struct | `services/core-api/internal/ingestion/store.go:20` |
| `Store` | struct | `services/core-api/internal/integrations/store.go:14` |
| `Store` | struct | `services/core-api/internal/journeys/store.go:34` |
| `Store` | struct | `services/core-api/internal/leads/store.go:10` |
| `Store` | struct | `services/core-api/internal/llm/store.go:14` |
| `Store` | struct | `services/core-api/internal/mapping/store.go:17` |
| `Store` | struct | `services/core-api/internal/models/store.go:30` |

## Highest-importance files

- `apps/web/src/app/(protected)/[locale]/_components/shellChrome.ts` (57 loc)
- `apps/web/src/app/(protected)/[locale]/_components/AppShell.tsx` (92 loc)
- `apps/web/src/app/api/leads/route.ts` (55 loc)
- `apps/web/src/app/api/tenant/offers/route.ts` (81 loc)
- `apps/web/src/app/api/tenant/approvals/workflows/route.ts` (50 loc)
- `apps/web/src/app/api/tenant/integrations/route.ts` (61 loc)
- `apps/web/src/app/api/tenant/model-studio/runs/route.ts` (77 loc)
- `apps/web/src/app/api/tenant/offers/[id]/versions/route.ts` (72 loc)
- `apps/web/src/app/api/tenant/ai/policy/route.ts` (39 loc)
- `apps/web/src/app/api/tenant/campaigns/route.ts` (67 loc)
- `apps/web/src/app/api/tenant/consent/events/route.ts` (41 loc)
- `apps/web/src/app/api/tenant/consent/policy/route.ts` (40 loc)
- `apps/web/src/app/api/tenant/models/[id]/versions/from-template/route.ts` (52 loc)
- `apps/web/src/app/api/tenant/models/[id]/versions/route.ts` (46 loc)
- `apps/web/src/app/api/tenant/onboarding/route.ts` (40 loc)
- `apps/web/src/app/api/platform-admin/tenants/route.ts` (33 loc)
- `apps/web/src/app/api/tenant/analytics/export/route.ts` (37 loc)
- `apps/web/src/app/api/tenant/analytics/views/route.ts` (35 loc)
- `apps/web/src/app/api/tenant/channels/config/route.ts` (40 loc)
- `apps/web/src/app/api/tenant/experiments/route.ts` (52 loc)
- `apps/web/src/app/api/tenant/segments/route.ts` (57 loc)
- `apps/web/src/app/api/auth/invite/accept/route.ts` (23 loc)
- `apps/web/src/app/api/auth/login/mfa/route.ts` (40 loc)
- `apps/web/src/app/api/auth/login/route.ts` (43 loc)
- `apps/web/src/app/api/tenant/decisions/route.ts` (36 loc)