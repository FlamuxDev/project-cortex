---
cortex-generated: true
title: background-worker-process
tags: [module]
---

# Background Worker Process

**Project:** [[mushagil]] | **Confidence:** verified | **verified@** `638838aad84d`
**Owns:** `apps/worker`

purpose: outbox relay, event consumers, scheduled sweeps, DLQ visibility, health endpoints.
path_prefixes: apps/worker
key_files: src/main.ts, src/outbox-worker.ts, src/trial-expiry-worker.ts, src/consumers/probe-created.consumer.ts, src/health-server.ts, src/dlq-metric.ts
entrypoints: bootstrapWorker() from src/main.ts; WORKER_HEALTH_PORT 3001 (/health/live, /health/ready)
responsibilities: EVENT_HANDLERS registry maps eventType→consumer; unknown event types logged and dropped safely; hourly trial sweep bounds EXPIRED staleness (<1 day) since BullMQ scheduler is skip-to-next (no replay backlog after outage).
invariants: graceful SIGTERM drain; relay uses mushagil_relay pool only.
pitfalls: only one real consumer exists (probe.created) — most outbox events currently have no consumer (by design until owning modules land).
confidence: verified

