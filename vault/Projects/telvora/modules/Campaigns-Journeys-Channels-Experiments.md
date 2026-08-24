---
cortex-generated: true
title: campaigns-journeys-channels-experiments
tags: [module]
---

# Campaigns, journeys, channels, experiments

**Project:** [[telvora]] | **Confidence:** verified | **verified@** `7423f040ed46`
**Owns:** `services/core-api/internal/{campaigns,journeys,channels,experiments}`

purpose: versioned campaigns with lifecycle (draft→validating→awaiting approval→running→completed/killed) + kill switch; event-driven journey DAGs with wait/split/goal nodes; channel adapters; A/B/control experiments with incremental attribution
path_prefixes: services/core-api/internal/{campaigns,journeys,channels,experiments}
key_files: internal/campaigns/{execution,ops}.go; internal/journeys/{dag,execution,worker}.go; internal/channels/{registry,sms,callback,retry}.go; internal/experiments/stats.go + result.go
entrypoints: campaigns start/pause/resume/kill/dispatches; journeys trigger-run/steps/kill; channels config/disable/callback; experiments start/complete/result
invariants: journey split outcomes are pure functions of (runID,personID)+branches — deterministic on replay, no assignment table (dag.go SplitBranch comment); kill switch must stop dispatch blast-radius visibly
pitfalls: e2e suite is concurrency-flaky around heavy mutations (see TESTS/GIT LESSONS)
confidence: verified

## Files (40+)

- `apps/web/src/app/(protected)/[locale]/app/admin/channels/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/journeys/[id]/builder/_components/JourneyBuilder.tsx`
- `apps/web/src/app/(protected)/[locale]/app/journeys/[id]/builder/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/journeys/[id]/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/journeys/[id]/runs/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/journeys/new/page.tsx`
- `apps/web/src/app/(protected)/[locale]/app/journeys/page.tsx`
- `apps/web/src/app/api/tenant/channels/config/[channel]/disable/route.ts`
- `apps/web/src/app/api/tenant/channels/config/route.ts`
- `apps/web/src/app/api/tenant/journeys/[id]/runs/route.ts`
- `apps/web/src/app/api/tenant/journeys/[id]/versions/[versionId]/publish/route.ts`
- `apps/web/src/app/api/tenant/journeys/[id]/versions/route.ts`
- `apps/web/src/app/api/tenant/journeys/route.ts`
- `apps/web/src/app/api/tenant/journeys/runs/[runId]/kill/route.ts`
- `apps/web/src/lib/channels.ts`
- `apps/web/src/lib/journeys.ts`
- `e2e/tests/channels.spec.ts`
- `e2e/tests/journeys.spec.ts`
- `services/core-api/internal/channels/callback.go`
- `services/core-api/internal/channels/callback_test.go`
- `services/core-api/internal/channels/handler.go`
- `services/core-api/internal/channels/model.go`
- `services/core-api/internal/channels/registry.go`
- `services/core-api/internal/channels/registry_test.go`
- `services/core-api/internal/channels/retry.go`

## API surface

- `GET locale`
- `GET secret`
- `GET fallbackChannel`
- `GET rateLimitPerMinute`
- `GET channel`
- `GET personId`
- `GET name`
- `GET reason`
- `GET journeyId`
- `POST /api/tenant/journeys/[id]/versions`
- `POST /api/tenant/journeys/[id]/runs`
- `POST /api/tenant/journeys`
- `POST /api/tenant/journeys/[id]/versions/[versionId]/publish`
- `POST /api/tenant/journeys/runs/[runId]/kill`
- `POST /api/tenant/channels/config/[channel]/disable`
