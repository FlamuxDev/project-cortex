---
cortex-generated: true
title: background-processing-tier
tags: [module]
---

# Background processing tier

**Project:** [[chat-agent-saas]] | **Confidence:** verified | **verified@** `d5c6955acca7`
**Owns:** `packages/api/src/jobs/`

purpose: all BullMQ processors + periodic sweeps, runnable standalone in prod.
path_prefixes: packages/api/src/jobs/
key_files: jobs/queue.ts (13 queues), jobs/workers/*.worker.ts (24 files incl. alertMonitor, retention, auditRetention, subscriptionPeriod, tokenRefresh, integrationPoll, outlookSubRenewal, connectionHealth, odooEnvSync, odooOperations), jobs/conversationTimeout.ts
entrypoints: src/workers-entry.ts (dist/workers-entry.js under PM2 chatagent-workers).
responsibilities: knowledge processing/sync, conversation analysis + timeout sweeps, analysis-backfill, subscription period rollover, alert monitoring, retention/RTBF purges, integration polling/token refresh/health, Odoo env sync + operation execution, 5 outreach pipelines, journey ticks, social publish/metrics.
invariants: MUST be registered in BOTH index.ts and workers-entry.ts or it silently skips one environment; providers registry imported side-effect-style in both.
pitfalls: single-instance assumption — Redis distributed locks make >1 replicas safe-ish but default is 1; queue records trimmed (200 complete/500 failed) to avoid unbounded growth.
confidence: verified

## Files (27+)

- `packages/api/src/jobs/conversationTimeout.ts`
- `packages/api/src/jobs/queue.ts`
- `packages/api/src/jobs/subscriptionPeriod.ts`
- `packages/api/src/jobs/workers/alertMonitor.worker.ts`
- `packages/api/src/jobs/workers/analysis.worker.ts`
- `packages/api/src/jobs/workers/auditRetention.test.ts`
- `packages/api/src/jobs/workers/auditRetention.worker.ts`
- `packages/api/src/jobs/workers/connectionHealth.worker.ts`
- `packages/api/src/jobs/workers/identityMemoryRetention.worker.ts`
- `packages/api/src/jobs/workers/integrationPoll.worker.ts`
- `packages/api/src/jobs/workers/journey.worker.ts`
- `packages/api/src/jobs/workers/knowledge.worker.test.ts`
- `packages/api/src/jobs/workers/knowledge.worker.ts`
- `packages/api/src/jobs/workers/knowledgeSync.worker.ts`
- `packages/api/src/jobs/workers/odooEnvSync.worker.ts`
- `packages/api/src/jobs/workers/odooOperations.worker.test.ts`
- `packages/api/src/jobs/workers/odooOperations.worker.ts`
- `packages/api/src/jobs/workers/outlookSubRenewal.worker.ts`
- `packages/api/src/jobs/workers/outreachCompose.worker.ts`
- `packages/api/src/jobs/workers/outreachImport.worker.ts`
- `packages/api/src/jobs/workers/outreachPush.worker.ts`
- `packages/api/src/jobs/workers/outreachSegment.worker.ts`
- `packages/api/src/jobs/workers/outreachSend.worker.ts`
- `packages/api/src/jobs/workers/retention.parse.test.ts`
- `packages/api/src/jobs/workers/retention.worker.ts`
