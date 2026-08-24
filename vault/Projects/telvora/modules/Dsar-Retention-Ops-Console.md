---
cortex-generated: true
title: dsar-retention-ops-console
tags: [module]
---

# DSAR, retention, ops console

**Project:** [[telvora]] | **Confidence:** verified | **verified@** `7423f040ed46`
**Owns:** `services/core-api/internal/{dsar,retention,ops}`

purpose: DSAR export/anonymization (real anonymization, not row deletion), retention sweeps, operations snapshot (queue depth, DLQ replay, decision latency, journey lag, channel errors)
path_prefixes: services/core-api/internal/{dsar,retention,ops}
key_files: dsar/store.go, retention/worker.go, ops/handler.go
entrypoints: dsar requests CRUD, ops/snapshot, ops/dead-messages/{id}/replay
confidence: verified

## Files (4+)

- `services/core-api/internal/ingestion/retention.go`
- `services/core-api/internal/ingestion/retention_test.go`
- `services/core-api/internal/retention/worker.go`
- `services/core-api/internal/retention/worker_test.go`
