---
cortex-generated: true
title: campify tests
tags: [tests/project]
---

# Campify — Test Map

71 test files.

| Kind | Count |
|---|---|
| e2e | 1 |
| integration | 16 |
| unit | 54 |

## e2e (1)

- `e2e/campaign.spec.ts`

## integration (16)

- `apps/worker/test/analyticsPipeline.integration.test.ts`
- `apps/worker/test/journeyPipeline.integration.test.ts`
- `apps/worker/test/pipeline.integration.test.ts`
- `apps/worker/test/webhookPipeline.integration.test.ts`
- `packages/core/test/analytics.integration.test.ts`
- `packages/core/test/approval.integration.test.ts`
- `packages/core/test/campaigns.integration.test.ts`
- `packages/core/test/crm.integration.test.ts`
- `packages/core/test/delivery.integration.test.ts`
- `packages/core/test/domain.integration.test.ts`
- `packages/core/test/journeys.integration.test.ts`
- `packages/core/test/plans.integration.test.ts`
- `packages/core/test/sales.integration.test.ts`
- `packages/core/test/salesTaskPipeline.integration.test.ts`
- `packages/core/test/webhooks.integration.test.ts`
- `packages/db/test/identity.integration.test.ts`

## unit (54)

- `apps/api/src/container.unit.test.ts`
- `apps/api/test/analyticsRoutes.contract.test.ts`
- `apps/api/test/api.contract.test.ts`
- `apps/api/test/apiReadRoutes.contract.test.ts`
- `apps/api/test/authz.contract.test.ts`
- `apps/api/test/campaigns.contract.test.ts`
- `apps/api/test/crmRoutes.contract.test.ts`
- `apps/api/test/deliveryRoutes.contract.test.ts`
- `apps/api/test/journeyRoutes.contract.test.ts`
- `apps/api/test/providerWebhookRoutes.contract.test.ts`
- `apps/api/test/salesTaskRoutes.contract.test.ts`
- `apps/api/test/webhookRoutes.contract.test.ts`
- `apps/web/src/app/api/login/route.unit.test.ts`
- `apps/web/src/app/api/signup/route.unit.test.ts`
- `apps/web/src/lib/i18n.unit.test.ts`
- `apps/web/src/lib/publicOrigin.unit.test.ts`
- `apps/web/test/smoke.e2e.test.ts`
- `apps/worker/src/container.unit.test.ts`
- `packages/adapters/ai-gemini/src/prompt.unit.test.ts`
- `packages/adapters/email-resend/src/index.unit.test.ts`
- `packages/adapters/fake/src/failure.unit.test.ts`
- `packages/adapters/queue-inprocess/src/index.contract.test.ts`
- `packages/adapters/webhook-http/src/index.contract.test.ts`
- `packages/config/src/index.unit.test.ts`
- `packages/core/src/analytics/abtest.unit.test.ts`
- `packages/core/src/analytics/attribution.unit.test.ts`
- `packages/core/src/analytics/roi.unit.test.ts`
- `packages/core/src/campaigns/objectives.unit.test.ts`
- `packages/core/src/campaigns/state.unit.test.ts`
- `packages/core/src/consent/gate.unit.test.ts`
- `packages/core/src/contacts/normalize.unit.test.ts`
- `packages/core/src/content/abTest.unit.test.ts`
- `packages/core/src/content/copilot.unit.test.ts`
- `packages/core/src/content/personalization.unit.test.ts`
- `packages/core/src/delivery/idempotency.unit.test.ts`
- `packages/core/src/delivery/quietHours.unit.test.ts`
- `packages/core/src/delivery/retry.unit.test.ts`
- `packages/core/src/identity/emails.unit.test.ts`
- `packages/core/src/identity/rbac.unit.test.ts`
- `packages/core/src/imports/import.unit.test.ts`
- `packages/core/src/imports/xlsx.unit.test.ts`
- `packages/core/src/journeys/graph.unit.test.ts`
- `packages/core/src/journeys/state.unit.test.ts`
- `packages/core/src/journeys/wait.unit.test.ts`
- `packages/core/src/sales/state.unit.test.ts`
- `packages/core/src/segments/compile.unit.test.ts`
- `packages/core/src/webhooks/inboundSigning.unit.test.ts`
- `packages/core/src/webhooks/signing.unit.test.ts`
- `packages/core/src/webhooks/urlGuard.unit.test.ts`
- `packages/db/test/all-tables.tenancy.test.ts`
- …and 4 more

## High-importance code with no obvious mapped test

_Heuristic (name/import match). Verify before treating as gaps._

- `apps/api/src/deliveryRoutes.ts`
- `apps/web/src/lib/actions.ts`
- `apps/api/src/campaignRoutes.ts`
- `apps/web/src/lib/api.ts`
- `apps/api/src/providerWebhookRoutes.ts`
- `apps/web/src/lib/campaign.ts`
- `apps/web/src/lib/importJob.ts`
- `scripts/plan.mjs`
- `apps/api/src/apiKeyAuth.ts`
- `apps/api/src/crmRoutes.ts`
- `apps/api/src/journeyRoutes.ts`
- `apps/web/src/lib/contact.ts`
- `apps/web/src/lib/locale.ts`
- `apps/worker/src/container.ts`
- `packages/adapters/ai-gemini/src/prompt.ts`
- `packages/core/src/analytics/abtest.ts`
- `packages/core/src/analytics/attribution.ts`
- `packages/core/src/analytics/roi.ts`
- `packages/core/src/campaigns/fingerprint.ts`
- `packages/core/src/campaigns/types.ts`
- `packages/core/src/consent/gate.ts`
- `packages/core/src/content/abTest.ts`
- `packages/core/src/delivery/providerEventIngest.ts`
- `packages/core/src/delivery/providerEvents.ts`
- `packages/core/src/delivery/quietHours.ts`
