---
cortex-generated: true
title: mcp-model-context-protocol
tags: [module]
---

# MCP (model context protocol)

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Org-level `McpServer` registry (transport http, authType none|header|bearer|oauth2_cc, secrets AES-encrypted, cached OAuth client-credentials tokens) × per-agent `AgentMcpServer` allowedTools (`schema.prisma:709-756`). Cached clients + header encryption in `services/mcp/client.ts`, `mcpAuth.ts`. Tools merged into the chat loop alongside native bundles (`chat.service.ts loadChatResources`).
- Client hardening unit-tested: auth-header injection (`client.authHeaders.test.ts`) and result deduplication (`client.dedupe.test.ts`). Tool schemas are pre-converted to Gemini-safe declarations before `bindTools` — LangChain's own converter emits JSON-Schema keywords Gemini 400s on, killing whole turns (`geminiToolSchema.ts`, comment at chat.service.ts:427-430; prod incident commit 2684c25).

