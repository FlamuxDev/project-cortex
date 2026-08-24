---
cortex-generated: true
title: commercial-limits
tags: [module]
---

# commercial limits

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `packages/core/src/plans,migrations 0033/0036/0037`

purpose: plan catalog + per-workspace overrides; atomic quota reservation for billed metrics.
path_prefixes: packages/core/src/plans, migrations 0033/0036/0037
key_files: packages/core/src/plans/repository.ts
entrypoints: reserveQuota/effectiveLimits called from dispatch + copilot metering; GET …/plan; platform_set_workspace_plan SECURITY DEFINER (operator-only, via `pnpm plan`)
responsibilities: null=unlimited convention; override-null=inherit-plan resolved once in effectiveLimits; monthly period windows; trial seats.
invariants: no payment gateway by decision — this protects margin only; ceilings changed only with database-owner access (deliberate posture, LAUNCH_READINESS §3).
confidence: verified

