---
cortex-generated: true
title: chat-pipeline-agent-runtime
tags: [module]
---

# Chat pipeline & agent runtime

**Project:** [[chat-agent-saas]] | **Confidence:** verified | **verified@** `d5c6955acca7`
**Owns:** `packages/api/src/modules/chat/,packages/api/src/services/ai/`

purpose: public + authenticated chat endpoints, the tool loop, streaming, quotas, handoff, safety screening.
path_prefixes: packages/api/src/modules/chat/, packages/api/src/services/ai/
key_files: modules/chat/chat.service.ts (2562 ln), chat.controller.ts, streamMarkerFilter.ts (+test), runToolLoop.usage.test.ts, services/ai/{modelProvider,geminiToolSchema,safetyScreening,memory,rag,resolveWorkspaceAi}.ts
entrypoints: POST /api/chat/* (public widget path, origin-checked); processMessage/processMessageStream/processPlaygroundMessage exports reused by playground and voiceLlm route.
responsibilities: conversation ownership, quota checks (assertMessageQuota/assertVoiceQuota), resource loading (RAG topK + MCP/custom-action/file/Odoo/Dynatrace/Splunk bundles), bounded tool loop with prompt-injection guards and tool-message pruning (pruneToolMessages 24k chars), SSE streaming with marker filtering, persistence + analysis enqueue.
invariants: markers filtered on the way OUT of the stream (split-across-tokens safe); empty completion must still produce a real answer (1852d96); every mutating route needs explicit authorize() (Viewer role exists); tool output wrapped as untrusted data before returning to model.
pitfalls: chat.service.ts is the hottest, largest file — changes ripple to voiceLlm.routes.ts which imports its internals (loadChatResources, buildSystemMessage, runToolLoop, computeScreening…); Gemini rejects reused/union JSON-schema subschemas (2684c25 prod incident) — sanitize via geminiToolSchema.ts; non-Gemini model ids were once silently rewritten to Gemini (header comment in modelProvider.ts).
confidence: verified

## Files (40+)

- `packages/api/src/modules/chat/chat.controller.streamError.test.ts`
- `packages/api/src/modules/chat/chat.controller.ts`
- `packages/api/src/modules/chat/chat.routes.ts`
- `packages/api/src/modules/chat/chat.schemas.ts`
- `packages/api/src/modules/chat/chat.service.screening.test.ts`
- `packages/api/src/modules/chat/chat.service.ts`
- `packages/api/src/modules/chat/conversation-ownership.test.ts`
- `packages/api/src/modules/chat/identity.routes.ts`
- `packages/api/src/modules/chat/invokeToolWithTimeout.test.ts`
- `packages/api/src/modules/chat/pruneToolMessages.test.ts`
- `packages/api/src/modules/chat/runToolLoop.llmTimeout.test.ts`
- `packages/api/src/modules/chat/runToolLoop.usage.test.ts`
- `packages/api/src/modules/chat/streamMarkerFilter.test.ts`
- `packages/api/src/modules/chat/streamMarkerFilter.ts`
- `packages/api/src/modules/chat/widget.routes.ts`
- `packages/api/src/services/ai/actingUserPrompt.test.ts`
- `packages/api/src/services/ai/chat.ts`
- `packages/api/src/services/ai/customActions.test.ts`
- `packages/api/src/services/ai/customActions.ts`
- `packages/api/src/services/ai/embeddings.ts`
- `packages/api/src/services/ai/fileTools.test.ts`
- `packages/api/src/services/ai/fileTools.ts`
- `packages/api/src/services/ai/geminiToolSchema.test.ts`
- `packages/api/src/services/ai/geminiToolSchema.ts`
- `packages/api/src/services/ai/knowledgeConflict.ts`

## API surface

- `PUT /:agentId/conversations/:conversationId/tags`
- `GET /:agentId/conversations/:conversationId/messages`
- `GET /:agentId/conversations`
- `POST /:agentId/playground/conversations/:conversationId/handoff`
- `POST /:agentId/playground/conversations/:conversationId/close`
- `POST /:agentId/playground/message`
- `POST /:agentId/upload-attachment`
- `GET /:agentId/conversations/:conversationId/export`
- `POST /:agentId/conversations/:conversationId/rating`
- `GET /:agentId/conversations/:conversationId/widget-messages`
- `POST /:agentId/conversations/:conversationId/handoff`
- `POST /:agentId/conversations/:conversationId/close`
- `POST /:agentId/stream`
- `POST /:agentId/message`
- `POST /:agentId/identity/revoke`
