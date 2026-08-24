---
cortex-generated: true
title: execution-engine-channels
tags: [module]
---

# execution engine & channels

**Project:** [[cvm]] | **Confidence:** verified | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/delivery/`

purpose: effectively-once send execution (ADR-010): claim row in delivery_attempt unique (tenant_id, dedupe_key) BEFORE provider call; four adapters (email/SMS/webhook + sandbox fixture); receipts parsing idempotent; retry classification; per-credential circuit breaker (NOT per provider — two tenants sharing a provider have different reputations); provider credentials encrypted.
path_prefixes: packages/modules/src/delivery/
key_files: application/send.ts, credentials.ts, receipts.ts, trace.ts; infrastructure/adapters.ts; domain/state.ts, adapter.ts
entrypoints: deliveryRoutes (/v1/deliveries/{id}, /v1/provider-credentials*, /v1/webhooks/delivery, /v1/templates*, /v1/channels, /v1/t/{token} tracker)
responsibilities: queued→submitted→delivered/failed/expired state machine; timeout classified `unknown` (retried EXACTLY once, cap is a constant); adapters speak raw HTTP not vendor SDKs so retries stay visible above the claim.
invariants: never-twice-by-us (a timeout leaves visible queued row); known-failed send may be RE-claimed under same row — without this the claim defeated retry and messages silently never sent (game day worst defect); ON CONFLICT DO NOTHING RETURNING not caught violation (25P02 aborts tx — bit twice).
confidence: verified

## Files (9+)

- `packages/modules/src/delivery/application/credentials.ts`
- `packages/modules/src/delivery/application/receipts.ts`
- `packages/modules/src/delivery/application/send.ts`
- `packages/modules/src/delivery/application/trace.ts`
- `packages/modules/src/delivery/domain/adapter.ts`
- `packages/modules/src/delivery/domain/state.ts`
- `packages/modules/src/delivery/http/routes.ts`
- `packages/modules/src/delivery/index.ts`
- `packages/modules/src/delivery/infrastructure/adapters.ts`

## API surface

- `GET /t/:token`
- `POST /webhooks/delivery/:provider`
- `GET /deliveries/:id`
- `DELETE /provider-credentials/:id`
- `POST /provider-credentials/:id/test`
- `PUT /provider-credentials`
- `GET /provider-credentials`
- `GET /channels`
- `GET /trace/:deliveryId`
