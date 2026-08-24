---
cortex-generated: true
title: end-user-identity-durable-memory
tags: [module]
---

# End-user identity & durable memory

**Project:** [[chat-agent-saas]] | **Confidence:** verified | **verified@** `d5c6955acca7`
**Owns:** `packages/api/src/services/identity/,packages/api/src/modules/identity/`

purpose: third auth concept (distinct from tenant JWT and platform-admin JWT): widget visitor identities, optionally verified via Odoo; sessions, assertions, RTBF retention.
path_prefixes: packages/api/src/services/identity/, packages/api/src/modules/identity/
key_files: services/identity/identity.service.ts (resolveIdentityBySessionId), modules/identity/*, ExternalIdentity/IdentitySession models, identityMemoryRetention.worker.ts
entrypoints: /api/chat/... identity routes (public), /api/identity admin router.
responsibilities: issue/bind sessions at call-start (stamped onto Conversation.identitySessionId), authorize Odoo end_user mode via actAs, gate durable cross-conversation memory facts to VERIFIED identities only.
invariants: anonymous visitors never get durable memory (trust boundary shared with Odoo end-user mode); identity always re-derived from our session id, never client-supplied token alone.
pitfalls: external_identity migration 20260731120000 added this late — older conversations lack identitySessionId (nullable everywhere).
confidence: verified

## Files (9+)

- `packages/api/src/modules/identity/identity.admin.routes.ts`
- `packages/api/src/services/identity/assertion.test.ts`
- `packages/api/src/services/identity/assertion.ts`
- `packages/api/src/services/identity/identity.memoryRetention.test.ts`
- `packages/api/src/services/identity/identity.service.test.ts`
- `packages/api/src/services/identity/identity.service.ts`
- `packages/api/src/services/identity/providers/odoo.identity.test.ts`
- `packages/api/src/services/identity/providers/odoo.identity.ts`
- `packages/api/src/services/identity/types.ts`

## API surface

- `POST /:id/purge-memory`
- `PUT /:id/retention`
- `GET /:id`
