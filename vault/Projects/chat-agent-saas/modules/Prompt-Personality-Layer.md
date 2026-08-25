---
cortex-generated: true
title: prompt-personality-layer
tags: [module]
---

# prompt & personality layer

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- `services/ai/personalityPrompt.ts` (455 lines) renders tone/language/customInstructions into the system prompt; compliance JSONB injects disclosure strings, restricted-topics and refusal rules — both unit-tested including a dedicated compliance test (`personalityPrompt.compliance.test.ts`).
- `buildSystemMessage` also stamps the real current date/time ("give the assistant the real current date and time", commit f829674), channel hints, vision instructions when enabled, acting-user personalization for verified identities (`actingUserPrompt.test.ts` covers roles/timezone/share claims rendering from `identity.service.ts:300-334`).
- Rolling memory: once history outgrows the live window, older turns fold into `Conversation.memorySummary` tracked by `memorySummarizedCount` so only new backlog is re-summarized (`schema.prisma:475-481`, `services/ai/memory.ts`). Durable cross-conversation facts merge into `ExternalIdentity.memory` **only** for verified identities (`analysis.worker.ts:209-224`).

