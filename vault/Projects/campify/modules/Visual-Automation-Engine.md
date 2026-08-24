---
cortex-generated: true
title: visual-automation-engine
tags: [module]
---

# visual automation engine

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `packages/core/src/journeys`

purpose: publishable node graphs (wait/send/task/branch/webhook) with enrollment and step execution.
path_prefixes: packages/core/src/journeys
key_files: packages/core/src/journeys/graph.ts, enroll.ts, execute.ts, wait.ts, state.ts, repository.ts
entrypoints: /v1/workspaces/:id/journeys* (draft/graph/publish/pause/resume/enrollments); worker ticks enrollDueContacts + executeStep
responsibilities: immutable published versions (DB triggers journey_version_immutable/journey_graph_immutable); entry criteria polled; step rows claimed like messages; a Send node INSERTS a messages row — the SAME queue/guards as campaigns, never a parallel send path (execute.ts header).
invariants: paused/stopped journeys excluded at discovery AND re-checked at execution; wait steps reschedule via scheduled_at; webhook nodes reuse the outbound-webhook infrastructure.
pitfalls: journey-originated messages have no campaign — LEFT JOIN semantics; quiet_hours_override defaults false for them (dispatch.ts:101).
confidence: verified

