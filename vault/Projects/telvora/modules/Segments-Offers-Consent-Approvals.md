---
cortex-generated: true
title: segments-offers-consent-approvals
tags: [module]
---

# Segments, offers, consent, approvals

**Project:** [[telvora]] | **Confidence:** verified | **verified@** `7423f040ed46`
**Owns:** `services/core-api/internal/{segments,offers,consent,approvals}`

purpose: rule-builder segments (AST → SQL, safelisted predicates), product catalog vs CVM offers, consent/contact-policy engine with suppressions, configurable separation-of-duties approval workflows
path_prefixes: services/core-api/internal/{segments,offers,consent,approvals}
key_files: internal/segments/{ast,translate,explain,drift}.go; internal/offers/{catalog,validate}.go; internal/consent/{evaluate,policy}.go; internal/approvals/store.go + notify.go
entrypoints: segments create/version/publish/preview/materialize/explain; offers versions/publish/submit-approval; consent events/policy/suppression; approvals requests/{id}/decide
invariants: segment attributes validated against closed Go registries before SQL construction — never dynamic column input (ast.go attributeFields); offer publish can require approval gate (offers/approval_gate_test.go); campaign dispatch always re-evaluates consent
pitfalls: segment SQL translation changes must keep explain-per-predicate parity (translate_test/explain_test)
confidence: verified

## Files (40+)

- `apps/web/src/app/(protected)/[locale]/app/admin/consent/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/offers/[id]/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/offers/new/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/offers/page.tsx`
- `apps/web/src/app/api/tenant/consent/bulk-import/route.ts`
- `apps/web/src/app/api/tenant/consent/events/route.ts`
- `apps/web/src/app/api/tenant/consent/policy/route.ts`
- `apps/web/src/app/api/tenant/consent/suppression/remove/route.ts`
- `apps/web/src/app/api/tenant/consent/suppression/route.ts`
- `apps/web/src/app/api/tenant/offers/[id]/redeem/route.ts`
- `apps/web/src/app/api/tenant/offers/[id]/versions/[versionId]/publish/route.ts`
- `apps/web/src/app/api/tenant/offers/[id]/versions/[versionId]/resubmit-approval/route.ts`
- `apps/web/src/app/api/tenant/offers/[id]/versions/[versionId]/submit-approval/route.ts`
- `apps/web/src/app/api/tenant/offers/[id]/versions/route.ts`
- `apps/web/src/app/api/tenant/offers/route.ts`
- `apps/web/src/lib/consent.ts`
- `apps/web/src/lib/offers.ts`
- `e2e/tests/consent.spec.ts`
- `e2e/tests/offers.spec.ts`
- `packages/ui/src/ConsentStatusPill.tsx`
- `services/core-api/internal/consent/evaluate.go`
- `services/core-api/internal/consent/evaluate_test.go`
- `services/core-api/internal/consent/handler.go`
- `services/core-api/internal/consent/model.go`
- `services/core-api/internal/consent/policy.go`

## API surface

- `GET confirmText`
- `GET rows`
- `GET locale`
- `GET source`
- `GET status`
- `GET legalBasis`
- `GET channel`
- `GET purpose`
- `GET personId`
- `GET profilingOptOutPurpose`
- `GET quietHoursTimezone`
- `GET quietHoursEnd`
- `GET quietHoursStart`
- `GET frequencyCapPeriodDays`
- `GET frequencyCapCount`
