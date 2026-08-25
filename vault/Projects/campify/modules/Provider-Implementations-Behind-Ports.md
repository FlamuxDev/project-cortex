---
cortex-generated: true
title: provider-implementations-behind-ports
tags: [module]
---

# provider implementations behind ports

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `packages/adapters`

purpose: fake (zero network), queue-inprocess (Postgres-as-queue), email-resend, ai-gemini, webhook-http.
path_prefixes: packages/adapters
key_files: packages/adapters/fake/src/index.ts, queue-inprocess/src/index.ts, email-resend/src/index.ts, ai-gemini/src/{index,prompt}.ts, webhook-http/src/index.ts
entrypoints: constructed in apps/*/src/container.ts
responsibilities: swap providers via container change only; audit:security gate fails if fake/ imports http clients.
invariants: fakes perform ZERO network I/O; real email requires BOTH key+from (half-configured ⇒ fake, never default-address sending).
pitfalls: queue visibility timeout coarse/fixed; ordering best-effort (ponytail comments name BullMQ upgrade path).
confidence: verified

## Files (11+)

- `packages/adapters/ai-gemini/src/index.ts`
- `packages/adapters/ai-gemini/src/prompt.ts`
- `packages/adapters/ai-gemini/src/prompt.unit.test.ts`
- `packages/adapters/email-resend/src/index.ts`
- `packages/adapters/email-resend/src/index.unit.test.ts`
- `packages/adapters/fake/src/failure.unit.test.ts`
- `packages/adapters/fake/src/index.ts`
- `packages/adapters/queue-inprocess/src/index.contract.test.ts`
- `packages/adapters/queue-inprocess/src/index.ts`
- `packages/adapters/webhook-http/src/index.contract.test.ts`
- `packages/adapters/webhook-http/src/index.ts`
