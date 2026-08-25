---
cortex-generated: true
title: analytics-quality-analysis
tags: [module]
---

# analytics / quality analysis

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Async per-conversation analysis (BullMQ, 3s delay, 4 attempts, 70s fixed backoff for Gemini 429) producing satisfaction/sentiment/lead/issues/QA sub-scores/frustration/churn + suggested FAQ (`jobs/workers/analysis.worker.ts:15-237`). The worker always calls `gemini-2.5-flash-lite` directly regardless of tenant chat provider — BYOK non-Gemini keys are deliberately ignored here to avoid 401s (comment 85-93). A backfill sweeper re-analyzes closed conversations that never got analyzed (`startAnalysisBackfillWorker`, `jobs/conversationTimeout.ts`).
- Alert rules/lock/metrics in `services/alerts/*` monitored by `alertMonitor.worker.ts` (quality-alert resolution flow: `ConversationAnalysis.qualityAlertResolvedAt/ById/Note` fields, schema 680-682).
- Tenant dashboards aggregate via `modules/analytics/analytics.routes.ts` (9 routes under `/api/agents/:agentId`); platform-wide roll-ups in `modules/platform/platform-analytics.*`. Conversation tags (GIN-indexed String[]) and rating fields power list filtering (`schema.prisma:471-474,496`). Runtime ops metrics (queue depth, per-route latency, 5xx counts) exposed unauthenticated at `/api/metrics` (`app.ts:240-277`).

