---
cortex-generated: true
title: http-plumbing-fastify
tags: [module]
---

# HTTP plumbing (Fastify)

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `apps/api/src (app.ts,rateLimit.ts,apiKeyAuth.ts,server.ts,container.ts)`

purpose: everything cross-cutting on the API: zod boundaries, error mapping, correlation ids, throttles, guards.
path_prefixes: apps/api/src (app.ts, rateLimit.ts, apiKeyAuth.ts, server.ts, container.ts)
key_files: apps/api/src/app.ts
entrypoints: buildApp(); server.ts binds API_PORT
responsibilities: see ARCHITECTURE; distinct client states for login failures; PG error codes mapped (40001→409 retry, timeouts→503, 23503→404 logged, 23505→409); driver errors logged structurally WITHOUT message/detail (PII).
invariants: correlation id always server-generated (client-supplied echoed separately — audit-log forgery otherwise); body limit 256KB globally, 20MB import-only with pre-read auth+membership guard.
pitfalls: rate limiter in-process (multiplies with N instances); authenticated throttles key on userId because BFF collapses IPs.
confidence: verified

## Files (3+)

- `apps/api/src/apiKeyAuth.ts`
- `apps/api/src/rateLimit.ts`
- `apps/api/src/server.ts`
