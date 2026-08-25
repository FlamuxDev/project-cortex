---
cortex-generated: true
title: agents-crud-config
tags: [module]
---

# agents CRUD + config

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- `modules/agents/agent.service.ts`: `createAgent` enforces subscription agentLimit inside a transaction creating Agent + AgentConfig (defaulting `compliance.voice.customLlm:true`) + an `AgentIntegration(platform='elevenlabs')` with generated apiKey/signingSecret, then best-effort syncs the remote ElevenLabs agent (`agent.service.ts:235-296`). Reads/writes are org-scoped (`getAgents(orgId)` etc., lines 302-381).
- `AgentConfig` (1:1) holds model/provider/systemPrompt/personality/appearance JSONB, compliance JSONB (rating/transcript/disclosure/voice.customLlm), vision settings, BYOK `apiKeyEncrypted`, voice fields (`schema.prisma:236-263`).
- Per-agent public surface security = origin allowlist stored in `appearance.allowedOrigins`; missing Origin is rejected when `requireOrigin` (state-changing/expensive public endpoints) — but note localhost origins are dev-only-gated (`agent-origin.service.ts:9-19,58-82`).

