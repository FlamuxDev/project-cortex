---
cortex-generated: true
title: analytics-models-decisions-opportunities-alerts
tags: [module]
---

# Analytics, models, decisions, opportunities, alerts

**Project:** [[telvora]] | **Confidence:** verified | **verified@** `7423f040ed46`
**Owns:** `services/core-api/internal/{analytics,models,decisions,opportunities,alerts,executive,ops}`

purpose: KPI semantic layer with A/B/C causal rigor grades; model registry/lifecycle/templates/monitoring; deterministic real-time NBA-NBO decision API with full trace; opportunity scout drafting; anomaly alerts with RCA assist; executive scorecard
path_prefixes: services/core-api/internal/{analytics,models,decisions,opportunities,alerts,executive,ops}
key_files: internal/models/{templates,studio,scoring,monitoring_compatibility,ml_client,worker}.go; internal/decisions/store.go (snapshot→policy→candidates→exclusions→scoring→arbitration→trace); internal/alerts/{detect,rca}.go; internal/opportunities/scout.go
entrypoints: analytics metrics/{key}; model-versions promote/score/monitor; POST tenant/decisions (real-time); opportunities scout; alerts detect
invariants: real-time decision NEVER depends on an LLM (RELEASE_NOTES.md); missing feature values degrade gracefully with trace chips, never fatal; model monitoring at 1M population uses bounded deterministic sampling (migration 0036 + monitoring_compatibility.go)
pitfalls: arbitration ordering is behavior — nil model versions have dedicated tests (nil_model_versions_test.go)
confidence: verified

## Files (40+)

- `apps/web/src/app/(protected)/[locale]/app/alerts/[id]/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/alerts/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/decisions/[id]/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/decisions/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/models/[id]/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/models/[id]/templates/[templateId]/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/models/[id]/templates/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/models/[id]/versions/[versionId]/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/models/new/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/models/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/opportunities/[id]/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/opportunities/page.tsx`
- `apps/web/src/app/api/tenant/alerts/[id]/assign-to-me/route.ts`
- `apps/web/src/app/api/tenant/alerts/[id]/status/route.ts`
- `apps/web/src/app/api/tenant/alerts/detect/route.ts`
- `apps/web/src/app/api/tenant/decisions/route.ts`
- `apps/web/src/app/api/tenant/executive/briefing/route.ts`
- `apps/web/src/app/api/tenant/models/[id]/rollback/route.ts`
- `apps/web/src/app/api/tenant/models/[id]/versions/from-template/route.ts`
- `apps/web/src/app/api/tenant/models/[id]/versions/route.ts`
- `apps/web/src/app/api/tenant/models/route.ts`
- `apps/web/src/app/api/tenant/models/versions/[versionId]/monitor/route.ts`
- `apps/web/src/app/api/tenant/models/versions/[versionId]/promote/route.ts`
- `apps/web/src/app/api/tenant/models/versions/[versionId]/score/route.ts`
- `apps/web/src/app/api/tenant/models/versions/[versionId]/submit-approval/route.ts`

## API surface

- `GET locale`
- `GET status`
- `GET purpose`
- `GET channel`
- `GET personId`
- `GET confirmText`
- `GET reason`
- `GET targetVersionId`
- `GET productCategory`
- `GET limitations`
- `GET algorithm`
- `GET populationSegmentId`
- `GET templateId`
- `GET horizonDays`
- `GET target`
