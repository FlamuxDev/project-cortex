---
cortex-generated: true
title: p8-p9-surface
tags: [module]
---

# P8/P9 surface

**Project:** [[cvm]] | **Confidence:** inferred | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/triggers|journeys|loyalty/`

purpose: trigger_rule evaluation (realtime dispatch listener in worker + batch fallback), journey builder/versions/instances/node-state, loyalty programs/tiers/ledger/redemptions/promotions, games/gamification participation. Present, wired, and screens shipped (commits 1a4baeb, 47ea930) though README lists journeys/loyalty as roadmap-absent-from-nav pre-P8 [uncertain which statement reflects current nav].
path_prefixes: packages/modules/src/triggers|journeys|loyalty/
entrypoints: triggerRoutes, journeyRoutes, loyaltyRoutes; TRIGGER/JOURNEY schedules registered; worker imports all three.
confidence: inferred

