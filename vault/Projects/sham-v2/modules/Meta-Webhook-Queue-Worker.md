---
cortex-generated: true
title: meta-webhook-queue-worker
tags: [module]
---

# Meta webhook + queue worker

**Project:** [[sham-v2]] | **Confidence:** inferred | **verified@** `71fbe7ede70c`
**Owns:** `src/channels/whatsapp/,src/channels/voice.js`

purpose: receive, dedupe, and answer WhatsApp traffic; media/voice support.
path_prefixes: src/channels/whatsapp/, src/channels/voice.js
key_files: webhook.js:31-55 (signature verify on RAW body → phone_number_id match → persistInbound → 200 immediately; processing never inline or Meta re-delivers 5×); worker.js (routing is two lines: active workflow? transition : ask(); everything sent via outbox for ordering/dedupe/retry); meta-client.js (signature/challenge/send); media.js (voice transcription/TTS)
entrypoints: POST/GET /api/webhooks/whatsapp
responsibilities: verification workflows (institution/teacher) driven through same worker; voice channel reuses the same ask() core (commit 4df74e2)
invariants: all inbound via inbox (provider_message_id PK = permanent dedupe, runtime/db.js:61-77); all outbound via delivery_outbox with idempotency_key UNIQUE (runtime/db.js:80-101)
confidence: high

## Files (8+)

- `src/channels/voice.js`
- `src/channels/whatsapp/delivery.js`
- `src/channels/whatsapp/inbound.js`
- `src/channels/whatsapp/media.js`
- `src/channels/whatsapp/meta-client.js`
- `src/channels/whatsapp/profiles.js`
- `src/channels/whatsapp/webhook.js`
- `src/channels/whatsapp/worker.js`

## API surface

- `GET X-Hub-Signature-256`
