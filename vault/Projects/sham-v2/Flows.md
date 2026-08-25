---
cortex-generated: true
title: sham-v2 flows
tags: [flows/project]
---

# sham-v2 — Product Flows

End-to-end behaviors as verified from source. Files are the evidence trail.

## API chat question
**Trigger:** POST /api/chat {message, session_id?, allow_contact?, user?}.
*[[sham-v2]] · confidence: high*

trigger: POST /api/chat {message, session_id?, allow_contact?, user?}.
steps: rate-limit → sanitize session/profile → clarify gate (`decideClarification` fires BEFORE any model call for ambiguous superlatives, asks exactly once, then defaults — index.js:363-377) → ranking-intent fast path answers clean measured-preference questions deterministically without Gemini (index.js:423-426) → LRU cache hit? return → Gemini plan → validateSql → zero rows? one review round → execute → renderAnswer (+ optional humanize) → finish() prefixes assumed-criterion disclosure → save history, respond (SQL shown to admins only).
files: src/channels/http/chat.controller.js, src/agent/index.js, src/agent/guard.js, src/agent/execute.js, src/agent/render.js, src/agent/clarify.js
confidence: high

**Files:**
- `src/channels/http/chat.controller.js`
- `src/agent/index.js`
- `src/agent/guard.js`
- `src/agent/execute.js`
- `src/agent/render.js`
- `src/agent/clarify.js`

## WhatsApp inbound message
**Trigger:** Meta webhook POST.
*[[sham-v2]] · confidence: high*

trigger: Meta webhook POST.
steps: raw-body HMAC verify → phone_number_id match → normalizeWebhook → INSERT into inbound_events (PK dedupe) → 200 within Meta's window → worker claims batch → routes: active workflow transition OR ask() → deliveries enqueued to delivery_outbox with idempotency keys → sender delivers to Graph API with retry/backoff.
files: src/channels/whatsapp/webhook.js, inbound.js, worker.js, delivery.js; src/runtime/outbox.js
confidence: high

**Files:**
- `src/channels/whatsapp/webhook.js`
- `inbound.js`
- `worker.js`
- `delivery.js; src/runtime/outbox.js`

## Catalog sync / generation swap
**Trigger:** cron scheduler pulls PGDMP backup (or manual `npm run sync`).
*[[sham-v2]] · confidence: high*

trigger: cron scheduler pulls PGDMP backup (or manual `npm run sync`).
steps: build-mode staging DB opened writable → import-backup restores via pg_restore → mirror builds relational tables → schema profiles rebuilt → activate: atomic pointer write → running service detects activation → graceful self-restart (SIGTERM-like shutdown flushes sessions/runtime first, server.js:33-57) → next boot opens new generation readonly.
files: src/db/build.js, src/db/pointer.js, src/sync/{pg-backup,import-backup,scheduler}.js, src/server.js
confidence: high

**Files:**
- `src/db/build.js`
- `src/db/pointer.js`
- `src/sync/{pg-backup`
- `import-backup`
- `scheduler}.js`
- `src/server.js`

## Guided school search (API only)
**Trigger:** parent mentions child + school intent (regex-gated, index.js:208-215).
*[[sham-v2]] · confidence: high*

trigger: parent mentions child + school intent (regex-gated, index.js:208-215).
steps: startGuidedSchool collects city/budget/system/child-gender → buildGuidedSchoolSql constructs parameterized-by-code SQL from the plan (never the model) → runSql through normal guard → top-3 rendered with institution action links + seat-booking follow-up.
files: src/agent/index.js:220-301, src/agent/guided.js, src/channels/http/chat.controller.js:91-140
confidence: high

**Files:**
- `src/agent/index.js:220-301`
- `src/agent/guided.js`
- `src/channels/http/chat.controller.js:91-140`
