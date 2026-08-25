---
cortex-generated: true
title: llm-ai-layer
tags: [module]
---

# LLM / AI layer

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Provider routing is real multi-provider: gemini/openai/anthropic specs with model-id shape checks, SystemConfig default models, per-provider key fallbacks, reasoning-model temperature quirk handling (`services/ai/modelProvider.ts:20-145`). Resolution order: agent BYOK key → org default key → platform SystemConfig key (`services/ai/resolveWorkspaceAi.ts:26-49`).
- Prompt assembly: `buildSystemMessage` (`chat.service.ts:188`) concatenates personality/compliance/grounding/memory/integration context — deliberately plain-string (LangChain template braces incident documented at 1142-1152). RAG context wrapped in escaped `<DOC>` tags with `KB_TRUST_GUARD` anti-injection instruction and `[ESCALATE_TO_HUMAN]` marker stripping (`services/ai/rag.ts:28-76`); tool outputs wrapped by `wrapToolOutput` with a `TOOL_OUTPUT_TRUST_GUARD` injected into the system prompt inside `runToolLoop` (`chat.service.ts:310,441-450`).
- Streaming: SSE from controller (`chat.controller.ts:48-88`); `streamMarkerFilter` strips internal markers from token stream; `runToolLoop` streams per iteration with fresh `AbortSignal.timeout(llmTimeout)`, falls back to non-streamed invoke on first-chunk crash, retries empty STOP completions twice with a nudge, prunes oversized tool messages (`pruneToolMessages`, 24000-char cap), and accumulates usage across iterations for billing (`chat.service.ts:422-683`).
- Quotas: `assertMessageQuota` counts user messages over a rolling 1-month window vs Subscription.messageLimit with Redis-deduped 70%/90% alerts (`chat.service.ts:867-923`); `assertVoiceQuota` analogous for voice minutes (924-1014).
- History: `loadChatHistory` caps the live window (CHAT_HISTORY_LIMIT=20, mirrored by voice's `VOICE_HISTORY_LIMIT` at voiceLlm.routes.ts:62) and re-hydrates image attachments for vision-enabled agents (`visionHistoryOptsFromConfig`, 684; per-index image allocation 711). Tool-message pruning keeps any single tool result ≤24k chars in-context (`pruneToolMessages`, 381).
- Failure laddering on empty model output, each fallback answering a *specific* known-empty case before a generic one: generated-file present → `fileReadyFallback`; tool calls present → last successful tool result; pending Odoo confirmation → `resolveOdooConfirmationFromReply`; else `EMPTY_RESPONSE_FALLBACK` (chat.service.ts:1728-1760).

