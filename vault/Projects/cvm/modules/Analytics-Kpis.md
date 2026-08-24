---
cortex-generated: true
title: analytics-kpis
tags: [module]
---

# analytics & KPIs

**Project:** [[cvm]] | **Confidence:** strongly_inferred | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/analytics/`

purpose: executive KPIs computed at read time; cohorts, behaviour funnels, trends, affinity, segment overlap, attribution comparison; panel naming what is deliberately NOT reported; unmeasurable renders as reason-not-zero.
path_prefixes: packages/modules/src/analytics/
key_files: application/, http/routes.ts
entrypoints: analyticsRoutes (/v1/analytics/executive|cohorts|behaviour-funnel|trend|affinity|segment-overlap|attribution-comparison)
confidence: strongly_inferred

## Files (10+)

- `packages/modules/src/analytics/application/attribution-comparison.ts`
- `packages/modules/src/analytics/application/attribution.ts`
- `packages/modules/src/analytics/application/experiment-analysis.ts`
- `packages/modules/src/analytics/application/explore.ts`
- `packages/modules/src/analytics/application/funnel.ts`
- `packages/modules/src/analytics/application/kpis.ts`
- `packages/modules/src/analytics/domain/attribution-models.ts`
- `packages/modules/src/analytics/domain/inference.ts`
- `packages/modules/src/analytics/http/routes.ts`
- `packages/modules/src/analytics/index.ts`

## API surface

- `GET /analytics/attribution-comparison`
- `GET /analytics/segment-overlap`
- `GET /analytics/affinity`
- `GET /analytics/trend`
- `GET /analytics/behaviour-funnel`
- `GET /analytics/cohorts`
- `GET /analytics/executive`
