---
cortex-generated: true
title: orgs-billing-rbac-system-config-notifications-files-reports-artifacts
tags: [module]
---

# Orgs, billing, RBAC, system config, notifications, files, reports/artifacts

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** `packages/api/src/modules/{organizations,platform,roles,team,auth,notifications,files,reports,analytics,booking,support,ai-studio,artifacts}/,packages/api/src/services/{plans,reports,email.ts,notifications.ts}`

purpose: tenant administration, custom billing/quota, plan catalog, platform-admin API surface, SystemConfig DB-backed settings, file generation, report artifacts.
path_prefixes: packages/api/src/modules/{organizations,platform,roles,team,auth,notifications,files,reports,analytics,booking,support,ai-studio,artifacts}/, packages/api/src/services/{plans,reports,email.ts,notifications.ts}
key_files: utils/config.ts (hot-reloaded SystemConfig + cluster invalidation), utils/orgFeatures.ts, middleware/orgFeature.ts, services/reports/artifacts.ts (untracked, +test), prisma/scripts/create-platform-admin.ts
entrypoints: /api/org, /api/platform (install gated by PLATFORM_INSTALL_TOKEN), /api/auth, /api/files, /api/artifacts, /api/reports.
responsibilities: Subscription rolling-period limits with threshold notifications; Plan/FeatureCatalog/PlanFeature dynamic plans; per-org feature flags resolved org.settings.features → plan catalog → hardcoded ORG_FEATURE_CATALOG seed in @chatagent/shared; CSV/Excel/PDF/Word generation (fileTools.ts) now upgraded to persisted ReportArtifact rows with provenance (in flight).
invariants: PlatformAdmin is a separate identity table + separate JWT secret (defaults derived from JWT_SECRET); first admin bootstrapped only while table empty; secrets encrypted via ENCRYPTION_KEY, decrypt at point of use only.
pitfalls: PUT /api/org/profile shipped without authorize() letting any member rename/rebrand workspace (CLAUDE.md lesson — check every mutating route); file links used to be effectively-permanent HMAC URLs with no lifecycle (audit finding #6).
confidence: verified (billing/RBAC), strongly_inferred (artifacts redesign)

## Files (40+)

- `packages/api/src/middleware/auth.ts`
- `packages/api/src/middleware/authRoleExpiry.test.ts`
- `packages/api/src/middleware/platformAuth.ts`
- `packages/api/src/middleware/platformSuper.ts`
- `packages/api/src/modules/ai-studio/ai.controller.ts`
- `packages/api/src/modules/ai-studio/ai.routes.ts`
- `packages/api/src/modules/ai-studio/ai.schemas.ts`
- `packages/api/src/modules/analytics/analytics.controller.ts`
- `packages/api/src/modules/analytics/analytics.report.controller.ts`
- `packages/api/src/modules/analytics/analytics.report.export.test.ts`
- `packages/api/src/modules/analytics/analytics.report.export.ts`
- `packages/api/src/modules/analytics/analytics.report.labels.ts`
- `packages/api/src/modules/analytics/analytics.report.service.ts`
- `packages/api/src/modules/analytics/analytics.routes.ts`
- `packages/api/src/modules/analytics/analytics.schemas.ts`
- `packages/api/src/modules/analytics/analytics.service.ts`
- `packages/api/src/modules/auth/auth.controller.ts`
- `packages/api/src/modules/auth/auth.cookies.ts`
- `packages/api/src/modules/auth/auth.routes.ts`
- `packages/api/src/modules/auth/auth.schemas.test.ts`
- `packages/api/src/modules/auth/auth.schemas.ts`
- `packages/api/src/modules/auth/auth.service.ts`
- `packages/api/src/modules/booking/booking.controller.ts`
- `packages/api/src/modules/booking/booking.public.routes.ts`
- `packages/api/src/modules/booking/booking.service.ts`

## API surface

- `POST /insights/:campaignId`
- `POST /predict`
- `POST /content/variants`
- `POST /content/ads`
- `POST /content/messages`
- `POST /campaign-studio/draft`
- `GET /:agentId/analytics/report/export`
- `GET /:agentId/analytics/report`
- `GET /:agentId/issues`
- `POST /:agentId/issues/:analysisId/reopen`
- `POST /:agentId/issues/:analysisId/resolve`
- `GET /:agentId/analytics/channels`
- `GET /:agentId/analytics/sentiment`
- `GET /:agentId/analytics/timeline`
- `GET /:agentId/analytics/overview`
