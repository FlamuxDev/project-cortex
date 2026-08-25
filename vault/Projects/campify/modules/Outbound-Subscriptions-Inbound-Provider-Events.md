---
cortex-generated: true
title: outbound-subscriptions-inbound-provider-events
tags: [module]
---

# outbound subscriptions + inbound provider events

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `packages/core/src/webhooks,packages/adapters/webhook-http,migrations 0029/0030`

purpose: signed outbound event delivery to customer URLs; HMAC-verified inbound Resend events.
path_prefixes: packages/core/src/webhooks, packages/adapters/webhook-http, migrations 0029/0030
key_files: packages/core/src/webhooks/dispatch.ts, signing.ts, inboundSigning.ts, urlGuard.ts, repository.ts
entrypoints: /v1/workspaces/:id/webhook-subscriptions*, /webhook-deliveries*(redeliver); POST /v1/providers/resend/webhook
responsibilities: emission wired into 8 domain events; HMAC signing incl. replay bounding; SSRF-guarded URL validation (urlGuard); delivery queue with redeliver.
invariants: raw-body bytes preserved for signature verification (app.ts:335 replaces JSON parser); secret absent ⇒ refuse everything (lose feature, not control); subscription secrets plaintext (must be readable to HMAC — flagged debt).
pitfalls: ANY non-2xx retries all 5 attempts (deleted endpoint burns budget; ponytail-flagged in dispatch.ts).
confidence: verified

## Files (10+)

- `packages/adapters/webhook-http/src/index.contract.test.ts`
- `packages/adapters/webhook-http/src/index.ts`
- `packages/core/src/webhooks/dispatch.ts`
- `packages/core/src/webhooks/inboundSigning.ts`
- `packages/core/src/webhooks/inboundSigning.unit.test.ts`
- `packages/core/src/webhooks/repository.ts`
- `packages/core/src/webhooks/signing.ts`
- `packages/core/src/webhooks/signing.unit.test.ts`
- `packages/core/src/webhooks/urlGuard.ts`
- `packages/core/src/webhooks/urlGuard.unit.test.ts`
