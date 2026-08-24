---
cortex-generated: true
title: platform-foundation-kernel
tags: [module]
---

# Platform Foundation Kernel

**Project:** [[mushagil]] | **Confidence:** verified | **verified@** `638838aad84d`
**Owns:** `packages/platform/src`

purpose: IDs/time/money/errors/correlation + unit-of-work, idempotency, outbox relay, queue wrapper, tenant fairness, provider-call guard.
path_prefixes: packages/platform/src
key_files: src/application/unit-of-work/unit-of-work.ts, src/infrastructure/unit-of-work/pg-transaction-runner.ts, src/infrastructure/outbox/outbox-relay.ts, src/infrastructure/outbox/bullmq-outbox-publisher.ts, src/infrastructure/queue/{queue-wrapper,processed-event-guard,scheduler}.ts, src/domain/errors/app-error.ts, src/domain/money/money.ts, src/domain/ids/id.ts (UUIDv7), src/domain/correlation/context.ts, src/domain/transaction-guard/guard.ts, src/domain/queue/tenant-fairness.ts
entrypoints: imported by every app/module; OutboxRelay driven by apps/worker/src/outbox-worker.ts
responsibilities: one canonical mutation pattern (mutate+audit+outbox in a single tx); exactly-once logical effects via processed_event ledger; idempotency keyed tenant+principal+operation+idempotency key+canonical request hash (src/domain/idempotency/canonical-hash.ts).
invariants: audit/outbox failure rolls back the domain mutation (proven tests/integration unit-of-work-atomicity.test.ts); FOR UPDATE SKIP LOCKED relay claim — 3 concurrent relays publish each event once (M01 evidence); provider calls forbidden while tx open.
pitfalls: QueueWrapper must duplicate() the Redis connection for the blocking worker (a shared connection once caused a consumer wake-up hang misattributed to the queue name — comment at apps/worker/src/outbox-worker.ts:14–20 documents this).
confidence: verified

