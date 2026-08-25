---
cortex-generated: true
title: external-identity-odoo-sso-into-chat
tags: [module]
---

# external identity (Odoo SSO into chat)

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Assertion exchange: `POST /api/chat/:agentId/identity/exchange` (origin-checked) → provider verify (JWS from Odoo addon) → upsert ExternalIdentity → mint 32-byte opaque token storing only SHA-256 hash; replay defence = UNIQUE `assertionJti` (`<installationId>:<jti>`) claimed by the insert itself (`services/identity/identity.service.ts:63-195`, P2002 → audit + reject).
- Session resolution returns a trusted context derived wholly from our DB; revoked/expired session or revoked identity ⇒ null; bound to the issuing agent (`identity.service.ts:205-248`).
- Durable per-person `memory` JSONB with retention purge worker + RTBF endpoint (`purgeExpiredMemory` 460-492, `purgeIdentityMemoryNow` 504-518, worker `jobs/workers/identityMemoryRetention.worker.ts`).
- Delegation keys (per-user Odoo execution credentials) AES-encrypted on the session, used to prove possession for per-operation grants (`DelegationInput` 55-61, `loadDelegation` 380-406).

