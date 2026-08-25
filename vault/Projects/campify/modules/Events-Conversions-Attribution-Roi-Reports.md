---
cortex-generated: true
title: events-conversions-attribution-roi-reports
tags: [module]
---

# events, conversions, attribution, ROI, reports

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `packages/core/src/analytics,packages/core/src/integrations/apiKeys.ts,apps/api/src/apiReadRoutes.ts`

purpose: API-key event ingestion, last-touch attribution, per-campaign reports + dashboard rollups.
path_prefixes: packages/core/src/analytics, packages/core/src/integrations/apiKeys.ts, apps/api/src/apiReadRoutes.ts
key_files: packages/core/src/analytics/attribution.ts, roi.ts, abtest.ts, repository.ts; apps/api/src/apiKeyAuth.ts; migrations 0024/0026/0035
entrypoints: POST …/events (Bearer API key), GET …/campaigns/:id/report(.csv), GET …/dashboard; partner read surface /v1/w/:id/{contacts,segments,campaigns,events,conversions} via requireApiKey
responsibilities: hash-only API keys (plaintext shown once); find_active_api_key SECURITY DEFINER lookup before tenant scope exists; conversion windowing vs most recent send; completeness flags — ROI WITHHELD, not guessed, when cost/revenue partial (§15.3); attribution model disclosed on every report.
invariants: attribution is last-touch in-campaign, explicitly labelled (D8 stand-in); usage_counters never decrease (DB function); workspace_plans revokes write from app role so no route can raise a ceiling (migration 0033/0036).
pitfalls: executiveDashboard is N+1 per campaign (ponytail-flagged, LAUNCH_READINESS §3).
confidence: verified

## Files (9+)

- `apps/api/src/apiReadRoutes.ts`
- `packages/core/src/analytics/abtest.ts`
- `packages/core/src/analytics/abtest.unit.test.ts`
- `packages/core/src/analytics/attribution.ts`
- `packages/core/src/analytics/attribution.unit.test.ts`
- `packages/core/src/analytics/repository.ts`
- `packages/core/src/analytics/roi.ts`
- `packages/core/src/analytics/roi.unit.test.ts`
- `packages/core/src/integrations/apiKeys.ts`
