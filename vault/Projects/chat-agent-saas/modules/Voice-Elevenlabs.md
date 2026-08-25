---
cortex-generated: true
title: voice-elevenlabs
tags: [module]
---

# voice / ElevenLabs

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Widget voice: signed-url / conversation-token exchange (`agent.service.ts:27-70`), transcript import on /stop (`widget.routes.ts` import + `voiceTranscript.ts`), post-call webhook with HMAC (`postCallWebhook.routes.ts`).
- **Custom LLM path** (this branch's namesake): `POST /api/voice-llm/...` implements the OpenAI-chat-completions-compatible contract ElevenLabs calls per turn; reuses the exact text-chat brain (RAG, MCP/Odoo bundles, safety screening, tool loop) with tighter budgets — 6 iterations, 12s tool timeout, 12s LLM timeout (`voiceLlm.routes.ts:62-78`, header comment 1-27). Auth is per-agent API key + signing secret via `loadActiveIntegration(agentId,'elevenlabs')` with constant-time compares (`timingSafeEqualStrings`, 55-60).
- Native MCP tool server for voice agents (booking/handoff tools) mounted at `/api/mcp/elevenlabs` authenticated per-agent API key (`services/elevenlabs/mcpServer.routes.ts`, `voiceMcp.ts`).

