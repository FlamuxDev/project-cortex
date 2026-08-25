---
cortex-generated: true
title: telvora api
tags: [api/project]
---

# Telvora — API Surface

397 routes. Grouped by owning file; every route names its handler.

## `apps/web/src/app/api/auth/forgot-password/route.ts`

- **POST** `/api/auth/forgot-password` → exported POST
- **GET** `email`
- **GET** `locale`

## `apps/web/src/app/api/auth/invite/accept/route.ts`

- **POST** `/api/auth/invite/accept` → exported POST
- **GET** `displayName`
- **GET** `locale`
- **GET** `password`
- **GET** `token`

## `apps/web/src/app/api/auth/login/mfa/route.ts`

- **POST** `/api/auth/login/mfa` → exported POST
- **GET** `challengeId`
- **GET** `code`
- **GET** `locale`
- **GET** `redirectTo`

## `apps/web/src/app/api/auth/login/route.ts`

- **POST** `/api/auth/login` → exported POST
- **GET** `email`
- **GET** `locale`
- **GET** `password`
- **GET** `redirectTo`

## `apps/web/src/app/api/auth/logout/route.ts`

- **POST** `/api/auth/logout` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/auth/reset-password/route.ts`

- **POST** `/api/auth/reset-password` → exported POST
- **GET** `locale`
- **GET** `password`
- **GET** `token`

## `apps/web/src/app/api/auth/signup/route.ts`

- **POST** `/api/auth/signup` → exported POST
- **GET** `locale`
- **GET** `organizationName`
- **GET** `ownerEmail`

## `apps/web/src/app/api/health/route.ts`

- **GET** `/api/health` → exported GET

## `apps/web/src/app/api/leads/route.ts`

- **POST** `/api/leads` → exported POST
- **GET** `company`
- **GET** `consent`
- **GET** `countryOrMarket`
- **GET** `email`
- **GET** `kind`
- **GET** `locale`
- **GET** `message`
- **GET** `name`
- **GET** `redirectTo`
- **GET** `role`
- **GET** `subject`

## `apps/web/src/app/api/platform-admin/tenants/[id]/reactivate/route.ts`
*module: [[telvora/modules/Identity-Tenancy-Rbac-Audit-Pii|identity-tenancy-rbac-audit-pii]]*

- **POST** `/api/platform-admin/tenants/[id]/reactivate` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/platform-admin/tenants/[id]/suspend/route.ts`
*module: [[telvora/modules/Identity-Tenancy-Rbac-Audit-Pii|identity-tenancy-rbac-audit-pii]]*

- **POST** `/api/platform-admin/tenants/[id]/suspend` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/platform-admin/tenants/route.ts`
*module: [[telvora/modules/Identity-Tenancy-Rbac-Audit-Pii|identity-tenancy-rbac-audit-pii]]*

- **POST** `/api/platform-admin/tenants` → exported POST
- **GET** `adminEmail`
- **GET** `displayName`
- **GET** `environmentLabel`
- **GET** `locale`
- **GET** `slug`

## `apps/web/src/app/api/tenant/ai/converse/route.ts`

- **POST** `/api/tenant/ai/converse` → exported POST
- **GET** `conversationId`
- **GET** `locale`
- **GET** `message`

## `apps/web/src/app/api/tenant/ai/policy/route.ts`

- **POST** `/api/tenant/ai/policy` → exported POST
- **GET** `allowedModels`
- **GET** `allowedPIIClasses`
- **GET** `fallbackModel`
- **GET** `locale`
- **GET** `maxContextTokens`
- **GET** `maxCostCents`
- **GET** `retentionDays`

## `apps/web/src/app/api/tenant/alerts/[id]/assign-to-me/route.ts`
*module: [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|analytics-models-decisions-opportunities-alerts]]*

- **POST** `/api/tenant/alerts/[id]/assign-to-me` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/alerts/[id]/status/route.ts`
*module: [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|analytics-models-decisions-opportunities-alerts]]*

- **POST** `/api/tenant/alerts/[id]/status` → exported POST
- **GET** `locale`
- **GET** `status`

## `apps/web/src/app/api/tenant/alerts/detect/route.ts`
*module: [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|analytics-models-decisions-opportunities-alerts]]*

- **POST** `/api/tenant/alerts/detect` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/analytics/export/route.ts`

- **POST** `/api/tenant/analytics/export` → exported POST
- **GET** `experimentId`
- **GET** `key`
- **GET** `locale`
- **GET** `route`
- **GET** `windowDays`

## `apps/web/src/app/api/tenant/analytics/views/route.ts`

- **POST** `/api/tenant/analytics/views` → exported POST
- **GET** `experimentId`
- **GET** `locale`
- **GET** `name`
- **GET** `route`
- **GET** `windowDays`

## `apps/web/src/app/api/tenant/approvals/requests/[id]/decide/route.ts`

- **POST** `/api/tenant/approvals/requests/[id]/decide` → exported POST
- **GET** `comment`
- **GET** `decision`
- **GET** `locale`

## `apps/web/src/app/api/tenant/approvals/workflows/[id]/archive/route.ts`

- **POST** `/api/tenant/approvals/workflows/[id]/archive` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/approvals/workflows/route.ts`

- **POST** `/api/tenant/approvals/workflows` → exported POST
- **GET** `locale`
- **GET** `name`
- **GET** `separationOfDuties`
- **GET** `slaHours`
- **GET** `stages`
- **GET** `subjectType`
- **GET** `thresholdField`
- **GET** `thresholdOperator`
- **GET** `thresholdValue`

## `apps/web/src/app/api/tenant/audit/verify/route.ts`
*module: [[telvora/modules/Identity-Tenancy-Rbac-Audit-Pii|identity-tenancy-rbac-audit-pii]]*

- **GET** `/api/tenant/audit/verify` → exported GET

## `apps/web/src/app/api/tenant/business-definitions/route.ts`

- **POST** `/api/tenant/business-definitions` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/campaigns/[id]/dry-run/route.ts`

- **POST** `/api/tenant/campaigns/[id]/dry-run` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/campaigns/[id]/start/route.ts`

- **POST** `/api/tenant/campaigns/[id]/start` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/campaigns/[id]/submit-approval/route.ts`

- **POST** `/api/tenant/campaigns/[id]/submit-approval` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/campaigns/route.ts`

- **POST** `/api/tenant/campaigns` → exported POST
- **GET** `budgetCents`
- **GET** `experimentRef`
- **GET** `locale`
- **GET** `name`
- **GET** `offerId`
- **GET** `segmentId`
- **GET** `smsBody`

## `apps/web/src/app/api/tenant/campaigns/runs/[runId]/kill/route.ts`

- **POST** `/api/tenant/campaigns/runs/[runId]/kill` → exported POST
- **GET** `campaignId`
- **GET** `locale`
- **GET** `reason`

## `apps/web/src/app/api/tenant/campaigns/runs/[runId]/pause/route.ts`

- **POST** `/api/tenant/campaigns/runs/[runId]/pause` → exported POST
- **GET** `campaignId`
- **GET** `locale`

## `apps/web/src/app/api/tenant/campaigns/runs/[runId]/resume/route.ts`

- **POST** `/api/tenant/campaigns/runs/[runId]/resume` → exported POST
- **GET** `campaignId`
- **GET** `locale`

## `apps/web/src/app/api/tenant/channels/config/[channel]/disable/route.ts`
*module: [[telvora/modules/Campaigns-Journeys-Channels-Experiments|campaigns-journeys-channels-experiments]]*

- **POST** `/api/tenant/channels/config/[channel]/disable` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/channels/config/route.ts`
*module: [[telvora/modules/Campaigns-Journeys-Channels-Experiments|campaigns-journeys-channels-experiments]]*

- **POST** `/api/tenant/channels/config` → exported POST
- **GET** `channel`
- **GET** `fallbackChannel`
- **GET** `locale`
- **GET** `rateLimitPerMinute`
- **GET** `secret`

## `apps/web/src/app/api/tenant/consent/bulk-import/route.ts`
*module: [[telvora/modules/Segments-Offers-Consent-Approvals|segments-offers-consent-approvals]]*

- **POST** `/api/tenant/consent/bulk-import` → exported POST
- **GET** `confirmText`
- **GET** `locale`
- **GET** `rows`

## `apps/web/src/app/api/tenant/consent/events/route.ts`
*module: [[telvora/modules/Segments-Offers-Consent-Approvals|segments-offers-consent-approvals]]*

- **POST** `/api/tenant/consent/events` → exported POST
- **GET** `channel`
- **GET** `legalBasis`
- **GET** `locale`
- **GET** `personId`
- **GET** `purpose`
- **GET** `source`
- **GET** `status`

## `apps/web/src/app/api/tenant/consent/policy/route.ts`
*module: [[telvora/modules/Segments-Offers-Consent-Approvals|segments-offers-consent-approvals]]*

- **POST** `/api/tenant/consent/policy` → exported POST
- **GET** `frequencyCapCount`
- **GET** `frequencyCapPeriodDays`
- **GET** `locale`
- **GET** `profilingOptOutPurpose`
- **GET** `quietHoursEnd`
- **GET** `quietHoursStart`
- **GET** `quietHoursTimezone`

## `apps/web/src/app/api/tenant/consent/suppression/remove/route.ts`
*module: [[telvora/modules/Segments-Offers-Consent-Approvals|segments-offers-consent-approvals]]*

- **POST** `/api/tenant/consent/suppression/remove` → exported POST
- **GET** `locale`
- **GET** `personId`

## `apps/web/src/app/api/tenant/consent/suppression/route.ts`
*module: [[telvora/modules/Segments-Offers-Consent-Approvals|segments-offers-consent-approvals]]*

- **POST** `/api/tenant/consent/suppression` → exported POST
- **GET** `locale`
- **GET** `personId`
- **GET** `reason`

## `apps/web/src/app/api/tenant/data-quality/detect/route.ts`

- **POST** `/api/tenant/data-quality/detect` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/data-quality/trust-policies/route.ts`

- **POST** `/api/tenant/data-quality/trust-policies` → exported POST
- **GET** `locale`
- **GET** `sourceSystem`
- **GET** `trustRank`

## `apps/web/src/app/api/tenant/decisions/route.ts`
*module: [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|analytics-models-decisions-opportunities-alerts]]*

- **POST** `/api/tenant/decisions` → exported POST
- **GET** `channel`
- **GET** `locale`
- **GET** `personId`
- **GET** `purpose`

## `apps/web/src/app/api/tenant/dsar/requests/route.ts`

- **POST** `/api/tenant/dsar/requests` → exported POST
- **GET** `locale`
- **GET** `personId`
- **GET** `requestType`

## `apps/web/src/app/api/tenant/executive/briefing/route.ts`
*module: [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|analytics-models-decisions-opportunities-alerts]]*

- **POST** `/api/tenant/executive/briefing` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/experiments/[id]/complete/route.ts`

- **POST** `/api/tenant/experiments/[id]/complete` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/experiments/[id]/start/route.ts`

- **POST** `/api/tenant/experiments/[id]/start` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/experiments/route.ts`

- **POST** `/api/tenant/experiments` → exported POST
- **GET** `attributionWindowDays`
- **GET** `controlSplitPercent`
- **GET** `hypothesis`
- **GET** `locale`
- **GET** `name`

## `apps/web/src/app/api/tenant/identity/candidates/[id]/approve/route.ts`
*module: [[telvora/modules/Connectors-Ingestion-Mapping-Quality-Identity-Resolution|connectors-ingestion-mapping-quality-identity-resolution]]*

- **POST** `/api/tenant/identity/candidates/[id]/approve` → exported POST
- **GET** `confirmText`
- **GET** `locale`

## `apps/web/src/app/api/tenant/identity/candidates/[id]/reject/route.ts`
*module: [[telvora/modules/Connectors-Ingestion-Mapping-Quality-Identity-Resolution|connectors-ingestion-mapping-quality-identity-resolution]]*

- **POST** `/api/tenant/identity/candidates/[id]/reject` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/identity/merges/[id]/reverse/route.ts`
*module: [[telvora/modules/Connectors-Ingestion-Mapping-Quality-Identity-Resolution|connectors-ingestion-mapping-quality-identity-resolution]]*

- **POST** `/api/tenant/identity/merges/[id]/reverse` → exported POST
- **GET** `confirmText`
- **GET** `locale`

## `apps/web/src/app/api/tenant/identity/run-matching/route.ts`
*module: [[telvora/modules/Connectors-Ingestion-Mapping-Quality-Identity-Resolution|connectors-ingestion-mapping-quality-identity-resolution]]*

- **POST** `/api/tenant/identity/run-matching` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/integrations/[id]/batch/route.ts`

- **POST** `/api/tenant/integrations/[id]/batch` → exported POST
- **GET** `file`
- **GET** `locale`
- **GET** `requiredColumns`

## `apps/web/src/app/api/tenant/integrations/[id]/mapping/dry-run/route.ts`
*module: [[telvora/modules/Connectors-Ingestion-Mapping-Quality-Identity-Resolution|connectors-ingestion-mapping-quality-identity-resolution]]*

- **POST** `/api/tenant/integrations/[id]/mapping/dry-run` → exported POST
- **GET** `locale`
- **GET** `mappingVersionId`
- **GET** `rawObjectId`

## `apps/web/src/app/api/tenant/integrations/[id]/mapping/run/route.ts`
*module: [[telvora/modules/Connectors-Ingestion-Mapping-Quality-Identity-Resolution|connectors-ingestion-mapping-quality-identity-resolution]]*

- **POST** `/api/tenant/integrations/[id]/mapping/run` → exported POST
- **GET** `locale`
- **GET** `mappingVersionId`
- **GET** `rawObjectId`

## `apps/web/src/app/api/tenant/integrations/[id]/mapping/versions/[versionId]/activate/route.ts`
*module: [[telvora/modules/Connectors-Ingestion-Mapping-Quality-Identity-Resolution|connectors-ingestion-mapping-quality-identity-resolution]]*

- **POST** `/api/tenant/integrations/[id]/mapping/versions/[versionId]/activate` → exported POST
- **GET** `locale`
- **GET** `rawObjectId`

## `apps/web/src/app/api/tenant/integrations/[id]/mapping/versions/route.ts`
*module: [[telvora/modules/Connectors-Ingestion-Mapping-Quality-Identity-Resolution|connectors-ingestion-mapping-quality-identity-resolution]]*

- **POST** `/api/tenant/integrations/[id]/mapping/versions` → exported POST
- **GET** `columns`
- **GET** `locale`
- **GET** `rawObjectId`

## `apps/web/src/app/api/tenant/integrations/[id]/pull/route.ts`

- **POST** `/api/tenant/integrations/[id]/pull` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/integrations/[id]/status/route.ts`

- **POST** `/api/tenant/integrations/[id]/status` → exported POST
- **GET** `locale`
- **GET** `status`

## `apps/web/src/app/api/tenant/integrations/[id]/test/route.ts`

- **POST** `/api/tenant/integrations/[id]/test` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/integrations/route.ts`

- **POST** `/api/tenant/integrations` → exported POST
- **GET** `capabilityType`
- **GET** `credentialValue`
- **GET** `freshnessSlaMinutes`
- **GET** `locale`
- **GET** `name`
- **GET** `newSourceSystemDescription`
- **GET** `newSourceSystemName`
- **GET** `scheduleFrequency`
- **GET** `sourceSystemId`

## `apps/web/src/app/api/tenant/invites/route.ts`

- **POST** `/api/tenant/invites` → exported POST
- **GET** `email`
- **GET** `locale`
- **GET** `role`

## `apps/web/src/app/api/tenant/journeys/[id]/runs/route.ts`
*module: [[telvora/modules/Campaigns-Journeys-Channels-Experiments|campaigns-journeys-channels-experiments]]*

- **POST** `/api/tenant/journeys/[id]/runs` → exported POST
- **GET** `locale`
- **GET** `personId`

## `apps/web/src/app/api/tenant/journeys/[id]/versions/[versionId]/publish/route.ts`
*module: [[telvora/modules/Campaigns-Journeys-Channels-Experiments|campaigns-journeys-channels-experiments]]*

- **POST** `/api/tenant/journeys/[id]/versions/[versionId]/publish` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/journeys/[id]/versions/route.ts`
*module: [[telvora/modules/Campaigns-Journeys-Channels-Experiments|campaigns-journeys-channels-experiments]]*

- **POST** `/api/tenant/journeys/[id]/versions` → exported POST

## `apps/web/src/app/api/tenant/journeys/route.ts`
*module: [[telvora/modules/Campaigns-Journeys-Channels-Experiments|campaigns-journeys-channels-experiments]]*

- **POST** `/api/tenant/journeys` → exported POST
- **GET** `locale`
- **GET** `name`

## `apps/web/src/app/api/tenant/journeys/runs/[runId]/kill/route.ts`
*module: [[telvora/modules/Campaigns-Journeys-Channels-Experiments|campaigns-journeys-channels-experiments]]*

- **POST** `/api/tenant/journeys/runs/[runId]/kill` → exported POST
- **GET** `journeyId`
- **GET** `locale`
- **GET** `reason`

## `apps/web/src/app/api/tenant/model-studio/runs/[id]/choose/route.ts`

- **POST** `/api/tenant/model-studio/runs/[id]/choose` → exported POST
- **GET** `locale`
- **GET** `versionId`

## `apps/web/src/app/api/tenant/model-studio/runs/route.ts`

- **POST** `/api/tenant/model-studio/runs` → exported POST
- **GET** `baselineAlgorithm`
- **GET** `candidateAlgorithm`
- **GET** `limitations`
- **GET** `locale`
- **GET** `name`
- **GET** `populationSegmentId`
- **GET** `productCategory`
- **GET** `targetMechanism`
- **GET** `useCase`

## `apps/web/src/app/api/tenant/models/[id]/rollback/route.ts`
*module: [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|analytics-models-decisions-opportunities-alerts]]*

- **POST** `/api/tenant/models/[id]/rollback` → exported POST
- **GET** `confirmText`
- **GET** `locale`
- **GET** `reason`
- **GET** `targetVersionId`

## `apps/web/src/app/api/tenant/models/[id]/versions/from-template/route.ts`
*module: [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|analytics-models-decisions-opportunities-alerts]]*

- **POST** `/api/tenant/models/[id]/versions/from-template` → exported POST
- **GET** `algorithm`
- **GET** `limitations`
- **GET** `locale`
- **GET** `populationSegmentId`
- **GET** `productCategory`
- **GET** `templateId`

## `apps/web/src/app/api/tenant/models/[id]/versions/route.ts`
*module: [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|analytics-models-decisions-opportunities-alerts]]*

- **POST** `/api/tenant/models/[id]/versions` → exported POST
- **GET** `algorithm`
- **GET** `horizonDays`
- **GET** `limitations`
- **GET** `locale`
- **GET** `populationSegmentId`
- **GET** `target`

## `apps/web/src/app/api/tenant/models/route.ts`
*module: [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|analytics-models-decisions-opportunities-alerts]]*

- **POST** `/api/tenant/models` → exported POST
- **GET** `locale`
- **GET** `name`
- **GET** `useCase`

## `apps/web/src/app/api/tenant/models/versions/[versionId]/monitor/route.ts`
*module: [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|analytics-models-decisions-opportunities-alerts]]*

- **POST** `/api/tenant/models/versions/[versionId]/monitor` → exported POST
- **GET** `locale`
- **GET** `registryId`

## `apps/web/src/app/api/tenant/models/versions/[versionId]/promote/route.ts`
*module: [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|analytics-models-decisions-opportunities-alerts]]*

- **POST** `/api/tenant/models/versions/[versionId]/promote` → exported POST
- **GET** `confirmText`
- **GET** `locale`
- **GET** `registryId`
- **GET** `targetState`

## `apps/web/src/app/api/tenant/models/versions/[versionId]/score/route.ts`
*module: [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|analytics-models-decisions-opportunities-alerts]]*

- **POST** `/api/tenant/models/versions/[versionId]/score` → exported POST
- **GET** `locale`
- **GET** `registryId`

## `apps/web/src/app/api/tenant/models/versions/[versionId]/submit-approval/route.ts`
*module: [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|analytics-models-decisions-opportunities-alerts]]*

- **POST** `/api/tenant/models/versions/[versionId]/submit-approval` → exported POST
- **GET** `locale`
- **GET** `registryId`

## `apps/web/src/app/api/tenant/offers/[id]/redeem/route.ts`
*module: [[telvora/modules/Segments-Offers-Consent-Approvals|segments-offers-consent-approvals]]*

- **POST** `/api/tenant/offers/[id]/redeem` → exported POST
- **GET** `locale`
- **GET** `personId`

## `apps/web/src/app/api/tenant/offers/[id]/versions/[versionId]/publish/route.ts`
*module: [[telvora/modules/Segments-Offers-Consent-Approvals|segments-offers-consent-approvals]]*

- **POST** `/api/tenant/offers/[id]/versions/[versionId]/publish` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/offers/[id]/versions/[versionId]/resubmit-approval/route.ts`
*module: [[telvora/modules/Segments-Offers-Consent-Approvals|segments-offers-consent-approvals]]*

- **POST** `/api/tenant/offers/[id]/versions/[versionId]/resubmit-approval` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/offers/[id]/versions/[versionId]/submit-approval/route.ts`
*module: [[telvora/modules/Segments-Offers-Consent-Approvals|segments-offers-consent-approvals]]*

- **POST** `/api/tenant/offers/[id]/versions/[versionId]/submit-approval` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/offers/[id]/versions/route.ts`
*module: [[telvora/modules/Segments-Offers-Consent-Approvals|segments-offers-consent-approvals]]*

- **POST** `/api/tenant/offers/[id]/versions` → exported POST
- **GET** `audienceSegmentId`
- **GET** `costModel`
- **GET** `incentiveDetail`
- **GET** `incentiveType`
- **GET** `locale`
- **GET** `redemptionCap`
- **GET** `validFrom`
- **GET** `validTo`

## `apps/web/src/app/api/tenant/offers/route.ts`
*module: [[telvora/modules/Segments-Offers-Consent-Approvals|segments-offers-consent-approvals]]*

- **POST** `/api/tenant/offers` → exported POST
- **GET** `audienceSegmentId`
- **GET** `costModel`
- **GET** `description`
- **GET** `incentiveDetail`
- **GET** `incentiveType`
- **GET** `locale`
- **GET** `name`
- **GET** `redemptionCap`
- **GET** `validFrom`
- **GET** `validTo`

## `apps/web/src/app/api/tenant/onboarding/route.ts`

- **POST** `/api/tenant/onboarding` → exported POST
- **GET** `currency`
- **GET** `defaultLanguage`
- **GET** `displayName`
- **GET** `locale`
- **GET** `retentionProfile`
- **GET** `timezone`

## `apps/web/src/app/api/tenant/opportunities/[id]/status/route.ts`
*module: [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|analytics-models-decisions-opportunities-alerts]]*

- **POST** `/api/tenant/opportunities/[id]/status` → exported POST
- **GET** `locale`
- **GET** `status`

## `apps/web/src/app/api/tenant/opportunities/scout/route.ts`
*module: [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|analytics-models-decisions-opportunities-alerts]]*

- **POST** `/api/tenant/opportunities/scout` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/ops/dead-messages/[id]/replay/route.ts`

- **POST** `/api/tenant/ops/dead-messages/[id]/replay` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/products/sync/route.ts`

- **POST** `/api/tenant/products/sync` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/roles/[id]/permissions/route.ts`

- **POST** `/api/tenant/roles/[id]/permissions` → exported POST
- **GET** `currentPassword`
- **GET** `locale`

## `apps/web/src/app/api/tenant/roles/route.ts`

- **POST** `/api/tenant/roles` → exported POST
- **GET** `currentPassword`
- **GET** `locale`
- **GET** `name`

## `apps/web/src/app/api/tenant/security/mfa/confirm/route.ts`

- **POST** `/api/tenant/security/mfa/confirm` → exported POST
- **GET** `code`
- **GET** `locale`

## `apps/web/src/app/api/tenant/security/mfa/disable/route.ts`

- **POST** `/api/tenant/security/mfa/disable` → exported POST
- **GET** `code`
- **GET** `currentPassword`
- **GET** `locale`

## `apps/web/src/app/api/tenant/security/mfa/enroll/route.ts`

- **POST** `/api/tenant/security/mfa/enroll` → exported POST
- **GET** `currentPassword`
- **GET** `locale`

## `apps/web/src/app/api/tenant/security/sessions/[id]/revoke/route.ts`

- **POST** `/api/tenant/security/sessions/[id]/revoke` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/segments/[id]/materialize/route.ts`

- **POST** `/api/tenant/segments/[id]/materialize` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/segments/[id]/preview/route.ts`

- **POST** `/api/tenant/segments/[id]/preview` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/segments/[id]/versions/route.ts`

- **POST** `/api/tenant/segments/[id]/versions` → exported POST
- **GET** `ast`
- **GET** `locale`

## `apps/web/src/app/api/tenant/segments/route.ts`

- **POST** `/api/tenant/segments` → exported POST
- **GET** `ast`
- **GET** `description`
- **GET** `locale`
- **GET** `mode`
- **GET** `name`

## `apps/web/src/app/api/tenant/simulator/runs/route.ts`

- **POST** `/api/tenant/simulator/runs` → exported POST
- **GET** `locale`
- **GET** `scale`
- **GET** `seed`

## `apps/web/src/app/api/tenant/simulator/wipe/route.ts`

- **POST** `/api/tenant/simulator/wipe` → exported POST
- **GET** `currentPassword`
- **GET** `locale`

## `apps/web/src/app/api/tenant/users/[id]/disable/route.ts`

- **POST** `/api/tenant/users/[id]/disable` → exported POST
- **GET** `currentPassword`
- **GET** `locale`

## `apps/web/src/app/api/tenant/users/[id]/reactivate/route.ts`

- **POST** `/api/tenant/users/[id]/reactivate` → exported POST
- **GET** `locale`

## `apps/web/src/app/api/tenant/users/[id]/role/route.ts`

- **POST** `/api/tenant/users/[id]/role` → exported POST
- **GET** `currentPassword`
- **GET** `locale`
- **GET** `roleId`

## `services/ml/app/main.py`

- **GET** `/healthz` → healthz
- **POST** `/monitor` → monitor
- **POST** `/score` → score
- **POST** `/train` → train
