---
cortex-generated: true
title: cloud-api-infrastructure
tags: [module]
---

# Cloud API infrastructure

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `packages/backend/src/whatsapp/`

purpose: all Graph API I/O + credential crypto + webhook verification.
path_prefixes: packages/backend/src/whatsapp/
key_files: client.ts (send + typing indicator/renewal), credentials.ts (AES-GCM decrypt, `plain:` fallback when WHATSAPP_TOKEN_ENC_KEY unset), webhook.ts (`verifyMetaWebhookSignature`, `resolveOrganizationFromWebhook` display#↔org), send-state.ts (outbound idempotency via inbound wamid, token probe cache, last_error flags), graph.ts, subscriptions.ts (`subscribeAppToWaba` — routes tenant WABA to our single app webhook), manual-discovery.ts, connection-ownership.ts, index.ts barrel
entrypoints: library
responsibilities: signature verification, send, typing, token lifecycle, subscription repair
invariants: per-org encrypted tokens only; no shared production WHATSAPP_ACCESS_TOKEN; no QR/Baileys path ever (ToS ban risk — explicit owner directive)
pitfalls: stored `whatsapp_status=verified` reflects save-time state — tokens expire later; probe cache must be cleared on reconnect
confidence: high

## Files (10+)

- `packages/backend/src/whatsapp/client.ts`
- `packages/backend/src/whatsapp/connection-ownership.ts`
- `packages/backend/src/whatsapp/credentials.ts`
- `packages/backend/src/whatsapp/graph.ts`
- `packages/backend/src/whatsapp/index.ts`
- `packages/backend/src/whatsapp/manual-discovery.ts`
- `packages/backend/src/whatsapp/send-state.ts`
- `packages/backend/src/whatsapp/subscriptions.ts`
- `packages/backend/src/whatsapp/webhook.test.ts`
- `packages/backend/src/whatsapp/webhook.ts`
