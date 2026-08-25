---
cortex-generated: true
title: telvora tests
tags: [tests/project]
---

# Telvora — Test Map

197 test files.

| Kind | Count |
|---|---|
| e2e | 40 |
| integration | 3 |
| unit | 154 |

## e2e (40)

- `e2e/playwright.config.ts`
- `e2e/tests/account-recovery.spec.ts` — covers 1 targets
- `e2e/tests/ai.spec.ts` — covers 1 targets
- `e2e/tests/alerts.spec.ts` — covers 1 targets
- `e2e/tests/analytics.spec.ts` — covers 1 targets
- `e2e/tests/app-shell.spec.ts`
- `e2e/tests/approvals.spec.ts` — covers 1 targets
- `e2e/tests/audit.spec.ts` — covers 1 targets
- `e2e/tests/auth.spec.ts`
- `e2e/tests/business-definitions.spec.ts` — covers 1 targets
- `e2e/tests/campaigns.spec.ts` — covers 1 targets
- `e2e/tests/channels.spec.ts` — covers 1 targets
- `e2e/tests/consent.spec.ts` — covers 1 targets
- `e2e/tests/customers.spec.ts` — covers 1 targets
- `e2e/tests/dataQuality.spec.ts` — covers 1 targets
- `e2e/tests/decisions.spec.ts` — covers 1 targets
- `e2e/tests/dev-ui.spec.ts`
- `e2e/tests/executive-home.spec.ts` — covers 1 targets
- `e2e/tests/experiments.spec.ts` — covers 1 targets
- `e2e/tests/health.spec.ts`
- `e2e/tests/helpers/coreApi.ts`
- `e2e/tests/identity.spec.ts` — covers 1 targets
- `e2e/tests/ingestion.spec.ts` — covers 1 targets
- `e2e/tests/integrations.spec.ts` — covers 1 targets
- `e2e/tests/journeys.spec.ts` — covers 1 targets
- `e2e/tests/landing.spec.ts`
- `e2e/tests/mapping.spec.ts` — covers 1 targets
- `e2e/tests/model-studio.spec.ts` — covers 1 targets
- `e2e/tests/model-templates.spec.ts` — covers 1 targets
- `e2e/tests/models.spec.ts` — covers 1 targets
- `e2e/tests/offers.spec.ts` — covers 1 targets
- `e2e/tests/opportunities.spec.ts` — covers 1 targets
- `e2e/tests/ops-console.spec.ts` — covers 1 targets
- `e2e/tests/privacy-security-hardening.spec.ts` — covers 1 targets
- `e2e/tests/segments.spec.ts` — covers 1 targets
- `e2e/tests/self-service-signup.spec.ts` — covers 1 targets
- `e2e/tests/seo.spec.ts`
- `e2e/tests/simulator.spec.ts` — covers 1 targets
- `e2e/tests/tenant-lifecycle.spec.ts` — covers 1 targets
- `e2e/tests/users-roles-admin.spec.ts` — covers 1 targets

## integration (3)

- `apps/web/src/app/api/tenant/integrations/[id]/test/route.ts`
- `services/core-api/internal/auth/integration_test.go`
- `services/core-api/internal/integrations/integrations_test.go`

## unit (154)

- `services/core-api/internal/alerts/detect_test.go`
- `services/core-api/internal/alerts/rca_test.go`
- `services/core-api/internal/alerts/rls_test.go`
- `services/core-api/internal/alerts/store_test.go`
- `services/core-api/internal/alerts/testutil_test.go`
- `services/core-api/internal/analytics/business_definitions_test.go`
- `services/core-api/internal/analytics/registry_test.go`
- `services/core-api/internal/analytics/rls_test.go`
- `services/core-api/internal/analytics/store_test.go`
- `services/core-api/internal/analytics/testutil_test.go`
- `services/core-api/internal/approvals/rls_test.go`
- `services/core-api/internal/approvals/store_test.go`
- `services/core-api/internal/approvals/testutil_test.go`
- `services/core-api/internal/audit/audit_test.go`
- `services/core-api/internal/auth/account_test.go`
- `services/core-api/internal/auth/mfa_login_test.go`
- `services/core-api/internal/auth/password_test.go`
- `services/core-api/internal/auth/rls_test.go`
- `services/core-api/internal/auth/security_handler_test.go`
- `services/core-api/internal/auth/token_test.go`
- `services/core-api/internal/auth/totp_test.go`
- `services/core-api/internal/campaigns/execution_test.go`
- `services/core-api/internal/campaigns/ops_test.go`
- `services/core-api/internal/campaigns/rls_test.go`
- `services/core-api/internal/campaigns/store_test.go`
- `services/core-api/internal/campaigns/testutil_test.go`
- `services/core-api/internal/channels/callback_test.go`
- `services/core-api/internal/channels/registry_test.go`
- `services/core-api/internal/channels/retry_test.go`
- `services/core-api/internal/channels/rls_test.go`
- `services/core-api/internal/channels/sms_test.go`
- `services/core-api/internal/channels/store_test.go`
- `services/core-api/internal/channels/testutil_test.go`
- `services/core-api/internal/consent/evaluate_test.go`
- `services/core-api/internal/consent/policy_test.go`
- `services/core-api/internal/consent/rls_test.go`
- `services/core-api/internal/consent/testutil_test.go`
- `services/core-api/internal/customer360/rls_test.go`
- `services/core-api/internal/customer360/store_test.go`
- `services/core-api/internal/customer360/testutil_test.go`
- `services/core-api/internal/dataquality/golden_test.go`
- `services/core-api/internal/dataquality/incidents_test.go`
- `services/core-api/internal/dataquality/rls_test.go`
- `services/core-api/internal/dataquality/scores_test.go`
- `services/core-api/internal/dataquality/testutil_test.go`
- `services/core-api/internal/db/url_test.go`
- `services/core-api/internal/decisions/arbitration_test.go`
- `services/core-api/internal/decisions/http_consent_test.go`
- `services/core-api/internal/decisions/latency_test.go`
- `services/core-api/internal/decisions/nil_model_versions_test.go`
- …and 104 more

## High-importance code with no obvious mapped test

_Heuristic (name/import match). Verify before treating as gaps._

- `apps/web/src/app/(protected)/[locale]/_components/shellChrome.ts`
- `apps/web/src/app/(protected)/[locale]/_components/AppShell.tsx`
- `packages/ui/src/cn.ts`
- `packages/ui/src/MonoValue.tsx`
- `apps/web/src/app/(protected)/[locale]/app/analytics/_components/MetricCard.tsx`
- `apps/web/src/app/(protected)/[locale]/_components/navItems.ts`
- `apps/web/src/app/(marketing)/[locale]/_content/docs.ts`
- `apps/web/src/app/(marketing)/[locale]/_content/resources.ts`
- `apps/web/src/app/(marketing)/[locale]/_content/solutions.ts`
- `packages/ui/src/Button.tsx`
- `packages/i18n/src/en.ts`
- `apps/web/src/app/(marketing)/[locale]/_components/LocaleSwitch.tsx`
- `apps/web/src/app/(protected)/[locale]/_components/NavRail.tsx`
- `apps/web/src/app/(protected)/[locale]/app/segments/_components/RuleBuilder.tsx`
- `apps/web/src/lib/auth.ts`
- `apps/web/src/lib/segments.ts`
- `infra/cdk/lib/foundation-stack.ts`
- `infra/cdk/lib/platform-stack.ts`
- `packages/i18n/src/ar.ts`
- `apps/web/src/app/(marketing)/[locale]/_components/Footer.tsx`
- `apps/web/src/app/(marketing)/[locale]/_components/Header.tsx`
- `apps/web/src/app/(marketing)/[locale]/_components/HeroProductPreview.tsx`
- `apps/web/src/app/(marketing)/[locale]/_components/MobileMenu.tsx`
- `apps/web/src/app/(marketing)/[locale]/_components/WebVitals.tsx`
- `apps/web/src/app/(protected)/[locale]/_components/CommandPalette.tsx`
