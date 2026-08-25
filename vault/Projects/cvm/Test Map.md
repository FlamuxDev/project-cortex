---
cortex-generated: true
title: cvm tests
tags: [tests/project]
---

# CVM — Test Map

50 test files.

| Kind | Count |
|---|---|
| e2e | 1 |
| unit | 49 |

## e2e (1)

- `e2e/golden-path.spec.ts`

## unit (49)

- `apps/api/__tests__/api.int.test.ts` — covers 1 targets
- `apps/api/__tests__/campaigns.int.test.ts` — covers 1 targets
- `apps/api/__tests__/cross-tenant-permissions.int.test.ts` — covers 1 targets
- `apps/api/__tests__/decisioning.int.test.ts` — covers 1 targets
- `apps/api/__tests__/delivery-idempotency.int.test.ts`
- `apps/api/__tests__/erasure.int.test.ts` — covers 1 targets
- `apps/api/__tests__/identity.int.test.ts` — covers 1 targets
- `apps/api/__tests__/ingestion.int.test.ts` — covers 1 targets
- `apps/api/__tests__/ml.int.test.ts` — covers 1 targets
- `apps/api/__tests__/profile.int.test.ts` — covers 1 targets
- `apps/api/__tests__/rate-limiting.int.test.ts` — covers 1 targets
- `apps/api/__tests__/role-catalogue.int.test.ts`
- `apps/api/__tests__/scim.int.test.ts` — covers 1 targets
- `apps/api/__tests__/segments.int.test.ts` — covers 1 targets
- `apps/web/__tests__/i18n.unit.test.ts` — covers 3 targets
- `ml/tests/test_train.py`
- `packages/modules/__tests__/advanced-intelligence.unit.test.ts`
- `packages/modules/__tests__/analytics-depth.int.test.ts`
- `packages/modules/__tests__/bandit.int.test.ts`
- `packages/modules/__tests__/behaviour-scores.int.test.ts`
- `packages/modules/__tests__/campaigns.unit.test.ts`
- `packages/modules/__tests__/connector-pull.int.test.ts` — covers 1 targets
- `packages/modules/__tests__/contract-validation.unit.test.ts` — covers 5 targets
- `packages/modules/__tests__/credentials.unit.test.ts` — covers 3 targets
- `packages/modules/__tests__/decision.unit.test.ts`
- `packages/modules/__tests__/entitlements.unit.test.ts`
- `packages/modules/__tests__/event-log.int.test.ts`
- `packages/modules/__tests__/features.unit.test.ts`
- `packages/modules/__tests__/fixtures/allow-private-hosts.ts`
- `packages/modules/__tests__/identifiers.unit.test.ts` — covers 1 targets
- `packages/modules/__tests__/inference.unit.test.ts`
- `packages/modules/__tests__/journeys.int.test.ts`
- `packages/modules/__tests__/journeys.unit.test.ts`
- `packages/modules/__tests__/loyalty-ledger.unit.test.ts`
- `packages/modules/__tests__/loyalty.int.test.ts`
- `packages/modules/__tests__/mfa.unit.test.ts`
- `packages/modules/__tests__/ml-skew.unit.test.ts`
- `packages/modules/__tests__/ml.unit.test.ts`
- `packages/modules/__tests__/model-ops.unit.test.ts`
- `packages/modules/__tests__/resolution.unit.test.ts` — covers 2 targets
- `packages/modules/__tests__/segments.unit.test.ts`
- `packages/modules/__tests__/triggers.unit.test.ts`
- `packages/platform/__tests__/dashboard-metrics.unit.test.ts`
- `packages/platform/__tests__/http-primitives.unit.test.ts` — covers 5 targets
- `packages/platform/__tests__/object-store.int.test.ts` — covers 1 targets
- `packages/platform/__tests__/redaction.unit.test.ts` — covers 1 targets
- `packages/platform/__tests__/telemetry.int.test.ts`
- `packages/platform/__tests__/tenant-isolation.int.test.ts` — covers 4 targets
- `packages/platform/__tests__/transactional-jobs.int.test.ts` — covers 3 targets

## High-importance code with no obvious mapped test

_Heuristic (name/import match). Verify before treating as gaps._

- `packages/modules/src/iam/http/admin-routes.ts`
- `packages/modules/src/loyalty/http/routes.ts`
- `packages/modules/src/ml/http/routes.ts`
- `packages/modules/src/campaigns/http/routes.ts`
- `packages/modules/src/segments/http/routes.ts`
- `packages/modules/src/ingestion/http/routes.ts`
- `apps/web/src/components/journey-builder.tsx`
- `apps/web/src/components/ui.tsx`
- `packages/modules/src/tenancy/http/routes.ts`
- `packages/modules/src/catalog/http/routes.ts`
- `packages/modules/src/journeys/http/routes.ts`
- `packages/modules/src/identity/http/routes.ts`
- `packages/modules/src/decision/http/routes.ts`
- `packages/modules/src/privacy/http/routes.ts`
- `packages/modules/src/delivery/http/routes.ts`
- `packages/modules/src/consent/http/routes.ts`
- `packages/modules/src/journeys/application/journeys.ts`
- `packages/modules/src/analytics/http/routes.ts`
- `packages/modules/src/iam/http/scim-routes.ts`
- `packages/modules/src/profile/http/routes.ts`
- `apps/web/src/components/rule-builder.tsx`
- `packages/modules/src/features/http/routes.ts`
- `packages/modules/src/iam/http/auth-routes.ts`
- `packages/platform/src/db/schema/_shared.ts`
- `packages/modules/src/experiments/http/routes.ts`
