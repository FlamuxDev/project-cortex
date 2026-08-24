---
cortex-generated: true
title: voice-calls-custom-llm-bridge-legacy-webhook-mcp-server
tags: [module]
---

# Voice calls (custom-LLM bridge, legacy webhook, MCP server)

**Project:** [[chat-agent-saas]] | **Confidence:** verified | **verified@** `d5c6955acca7`
**Owns:** `packages/api/src/services/elevenlabs/`

purpose: wire ElevenLabs Conversational AI agents to Botify brains; sync agent config/prompts/knowledge; import transcripts.
path_prefixes: packages/api/src/services/elevenlabs/
key_files: voiceLlm.routes.ts (custom-LLM endpoint, +test), agentConfigSync.ts (+agentConfigSync.customLlm.test.ts), voiceMcp.ts + mcpServer.routes.ts (+test), voiceTools.ts (legacy webhook tool), voiceTranscript.ts (post-call importer, dedupes metadata.source==='voice'), voicePrompt.ts, sourceSyncRunner.ts
entrypoints: POST /api/voice-llm/:agentId/completions AND /completions/chat/completions (both required — see pitfalls); POST /api/mcp/elevenlabs/:agentId (StreamableHTTP MCP).
responsibilities: per-turn OpenAI-SSE completions using the same brain as text chat; safety screening with useClassifier:false (latency); deterministic pending-action confirmation resolution; escalation handling with bilingual spoken fallback lines; message persistence tagged for transcript dedupe; agent provisioning/sync to ElevenLabs incl. custom_llm.url + ConvAI dynamic variables.
invariants: customLlm only for compliance.voice.customLlm===true agents (defense in depth); conversation correlation via OUR session row, never client-supplied identity tokens; VOICE budgets: 6 iterations, 12s tool timeout, 12s LLM timeout (dead air is the failure mode); already-handed-off conversations get empty utterance, never re-engaged.
pitfalls: the 404-every-turn bug — ElevenLabs appends `/chat/completions` to the base URL, so real turns hit `.../completions/chat/completions`; matching only the un-suffixed path broke EVERY call from day one until 49d4d73; IVC (Instant Voice Clone) voices cannot use custom_llm → automatic runtime fallback to legacy path (f9bd6d5); memory context was once missing here despite header claiming parity (fixed 3cee4ad).
confidence: verified

## Files (18+)

- `packages/api/src/services/elevenlabs/agentConfigSync.customLlm.test.ts`
- `packages/api/src/services/elevenlabs/agentConfigSync.ts`
- `packages/api/src/services/elevenlabs/agentSync.ts`
- `packages/api/src/services/elevenlabs/knowledgeSync.ts`
- `packages/api/src/services/elevenlabs/mcpServer.routes.test.ts`
- `packages/api/src/services/elevenlabs/mcpServer.routes.ts`
- `packages/api/src/services/elevenlabs/sourceSyncRunner.ts`
- `packages/api/src/services/elevenlabs/voice.test.ts`
- `packages/api/src/services/elevenlabs/voice.ts`
- `packages/api/src/services/elevenlabs/voiceLlm.routes.test.ts`
- `packages/api/src/services/elevenlabs/voiceLlm.routes.ts`
- `packages/api/src/services/elevenlabs/voiceMcp.ts`
- `packages/api/src/services/elevenlabs/voicePrompt.test.ts`
- `packages/api/src/services/elevenlabs/voicePrompt.ts`
- `packages/api/src/services/elevenlabs/voiceTools.test.ts`
- `packages/api/src/services/elevenlabs/voiceTools.ts`
- `packages/api/src/services/elevenlabs/voiceTranscript.test.ts`
- `packages/api/src/services/elevenlabs/voiceTranscript.ts`

## API surface

- `GET /api/mcp/elevenlabs/agent-1/mcp`
- `POST /api/mcp/elevenlabs/agent-1/mcp`
- `USE /api/mcp/elevenlabs`
- `DELETE /:agentId/mcp`
- `GET /:agentId/mcp`
- `POST /:agentId/mcp`
- `POST /api/voice-llm/agent-1/completions`
- `POST /api/voice-llm/agent-1/completions/chat/completions`
