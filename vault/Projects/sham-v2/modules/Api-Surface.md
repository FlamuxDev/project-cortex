---
cortex-generated: true
title: api-surface
tags: [module]
---

# API surface

**Project:** [[sham-v2]] | **Confidence:** inferred | **verified@** `71fbe7ede70c`
**Owns:** `src/app.js,src/channels/http/`

purpose: thin REST adapter; session hygiene; admin-only SQL disclosure.
path_prefixes: src/app.js, src/channels/http/
key_files: app.js:70-77 (routes); chat.controller.js:102-174 (POST /api/chat — sanitizes session id, reserves `wa_` prefix for WhatsApp, merges sanitized user profile {name, location}, caps history at 8 turns); chat.controller.js:169 (sql/attempts/ms only returned when req.isAdmin)
entrypoints: npm start → src/server.js → app.listen
responsibilities: rate limiting (chatLimiter), CORS allowlist from env (shamsieh.education/apr365.com per docs/API.md), helmet, trust-proxy config
invariants: channel identity never read from request body (AGENTS.md); raw-body webhook ordering (app.js:57-66)
confidence: high

## Files (4+)

- `src/app.js`
- `src/channels/http/chat.controller.js`
- `src/channels/http/middlewares.js`
- `src/channels/http/system.controller.js`

## API surface

- `GET /api/health`
- `GET /api/config`
- `GET /api/webhooks/whatsapp`
- `GET /api/voice/status`
- `GET /api/voice/auth`
- `POST /api/voice/tools/ask`
- `POST /api/chat`
- `POST /api/webhooks/whatsapp`
- `GET X-Admin-Key`
