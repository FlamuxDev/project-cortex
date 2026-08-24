---
cortex-generated: true
title: ingestion-contracts-quarantine-quality
tags: [module]
---

# ingestion, contracts, quarantine, quality

**Project:** [[cvm]] | **Confidence:** verified | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/ingestion/`

purpose: data sources/contracts, batch file ingest, eight §7.3 quality detections, quarantine with reasons + replay, event-type/schema registry, retention.
path_prefixes: packages/modules/src/ingestion/
key_files: application/, infrastructure/, http/routes.ts, jobs.ts
entrypoints: ingestionRoutes (/v1/ingest/*, /v1/data-contracts*, /v1/data-quality*)
responsibilities: validate against contracts before accept; duplicates counted not accepted (re-ingest → 0 accepted/25 duplicates); late events land in correct monthly partition with late_count.
invariants: batch counters exactly-once under concurrent runners (fixed a7907e9); ingestion key cannot rewrite its validating contract (e2e negative test).
pitfalls: stale-source metric didn't exist until game-day scenario 1 demanded it.
confidence: verified

## Files (20+)

- `packages/modules/src/ingestion/application/batches.ts`
- `packages/modules/src/ingestion/application/connector-pull.ts`
- `packages/modules/src/ingestion/application/pipeline.ts`
- `packages/modules/src/ingestion/application/projection.ts`
- `packages/modules/src/ingestion/application/pull.ts`
- `packages/modules/src/ingestion/application/quality.ts`
- `packages/modules/src/ingestion/application/quarantine.ts`
- `packages/modules/src/ingestion/application/registry.ts`
- `packages/modules/src/ingestion/domain/contract.ts`
- `packages/modules/src/ingestion/domain/ports.ts`
- `packages/modules/src/ingestion/domain/redaction.ts`
- `packages/modules/src/ingestion/domain/time.ts`
- `packages/modules/src/ingestion/domain/validate.ts`
- `packages/modules/src/ingestion/http/routes.ts`
- `packages/modules/src/ingestion/index.ts`
- `packages/modules/src/ingestion/infrastructure/connectors.ts`
- `packages/modules/src/ingestion/infrastructure/egress.ts`
- `packages/modules/src/ingestion/infrastructure/event-sink.ts`
- `packages/modules/src/ingestion/infrastructure/reader.ts`
- `packages/modules/src/ingestion/jobs.ts`

## API surface

- `GET /data-quality/contract-vocabulary`
- `GET /data-quality/metrics`
- `GET /data-quality/reasons`
- `GET /data-quality/sources`
- `POST /event-types`
- `GET /event-types`
- `POST /data-contracts/:id/activate`
- `GET /data-contracts/:id`
- `POST /data-contracts`
- `GET /data-contracts`
- `PATCH /data-sources/:id`
- `GET /data-sources/:id`
- `POST /data-sources`
- `GET /data-sources`
- `POST /ingest/errors/replay`
