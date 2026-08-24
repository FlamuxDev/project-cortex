---
cortex-generated: true
title: whatsapp-inbound-meta-channels
tags: [module]
---

# whatsapp-inbound & meta-channels

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `packages/ai/src/application/whatsapp-inbound/,meta-channels/`

purpose: drive the agent from channel events; keep backend free of ai imports.
path_prefixes: packages/ai/src/application/whatsapp-inbound/, meta-channels/
key_files: whatsapp-inbound/handle-inbound.ts (`generateAndSendAiReplyForInbound`: ai_handled gate :84, wamid idempotency :89/:131, 1800ms debounce :28/:94, token probe :107, typing renewal, send + persist outbound + usage_stats), index.ts; meta-channels/handle-inbound.ts (`handleMetaChannelInbound` — resolve→record only, typed outcomes, TODO plug point for AI reply)
invariants: pure orchestration; send-state plumbing lives in backend/whatsapp/send-state.ts
confidence: high

## Files (3+)

- `packages/ai/src/application/meta-channels/handle-inbound.ts`
- `packages/ai/src/application/whatsapp-inbound/handle-inbound.ts`
- `packages/ai/src/application/whatsapp-inbound/index.ts`
