---
cortex-generated: true
title: chat-agent-saas
tags: [project]
---

# chat-agent-saas

**Path:** `/home/aboud/Dev/chat-agent-saas`  
**Kind:** monorepo | **Languages:** .ts,.tsx,.sql,.py | **Frameworks:** None

**HEAD:** `d5c6955acca7` | **Brain:** `d5c6955acca7` | FRESH

| Files | Symbols | Modules | Flows | APIs | DB | Tests | Decisions | Memories |
|---|---|---|---|---|---|---|---|---|
| 957 | 4589 | 13 | 5 | 551 | 135 | 161 | 10 | 21 (0 stale) |

## Modules
- [[chat-agent-saas/modules/Background-Processing-Tier|Background processing tier]] — all BullMQ processors + periodic sweeps, runnable standalone in prod. [verified]
- [[chat-agent-saas/modules/Botify-Odoo-Module-Python|Botify Odoo module (Python)]] — in-Odoo addon providing signed nonce auth, delegation, policy enforcement at the source, so end-user [inferred]
- [[chat-agent-saas/modules/Campaigns-Journeys-Audiences-Push-Social|Campaigns, journeys, audiences, push, social]] — multi-channel outbound marketing (email/push/social/WhatsApp/SMS lineage), segments, journeys automa [inferred]
- [[chat-agent-saas/modules/Chat-Pipeline-Agent-Runtime|Chat pipeline & agent runtime]] — public + authenticated chat endpoints, the tool loop, streaming, quotas, handoff, safety screening. [verified]
- [[chat-agent-saas/modules/Embeddable-Chat-Widget|Embeddable chat widget]] — dependency-light vanilla-TS embeddable widget: chat, image upload, voice, handoff, per-agent theming [verified]
- [[chat-agent-saas/modules/End-User-Identity-Durable-Memory|End-user identity & durable memory]] — third auth concept (distinct from tenant JWT and platform-admin JWT): widget visitor identities, opt [verified]
- [[chat-agent-saas/modules/Knowledge-Ingestion-Rag|Knowledge ingestion & RAG]] — per-tenant knowledge sources → extraction → chunking → embeddings → pgvector retrieval; suggestions; [inferred]
- [[chat-agent-saas/modules/Odoo-Dynatrace-Splunk-Mcp-Channel-Providers|Odoo / Dynatrace / Splunk / MCP / channel providers]] — native tool adapters + OAuth/connection lifecycle for customer systems; capability discovery; eviden [inferred]
- [[chat-agent-saas/modules/Orgs-Billing-Rbac-System-Config-Notifications-Files-Reports-Artifacts|Orgs, billing, RBAC, system config, notifications, files, reports/artifacts]] — tenant administration, custom billing/quota, plan catalog, platform-admin API surface, SystemConfig  [inferred]
- [[chat-agent-saas/modules/Platform-Owner-Console|Platform owner console]] — manage orgs, billing, system config, feature catalog, integration tokens; separate identity + noinde [strongly_inferred]
- [[chat-agent-saas/modules/Shared-Types-Ci-Deploy-Tooling|Shared types, CI, deploy tooling]] — cross-package constants/types (systemConfigKeys.ts, ORG_FEATURE_CATALOG); deploy scripts with guardr [verified]
- [[chat-agent-saas/modules/Tenant-Web-App-Next-Js-16|Tenant web app (Next.js 16)]] — auth screens + full dashboard (agents, conversations, analytics, knowledge, integrations UI, outreac [verified]
- [[chat-agent-saas/modules/Voice-Calls-Custom-Llm-Bridge-Legacy-Webhook-Mcp-Server|Voice calls (custom-LLM bridge, legacy webhook, MCP server)]] — wire ElevenLabs Conversational AI agents to Botify brains; sync agent config/prompts/knowledge; impo [verified]

## Flows
- **Text chat turn (public widget or dashboard)** — user sends message via REST/SSE.
- **Voice call turn (custom-LLM path** — ElevenLabs Conversational AI agent POSTs OpenAI-shaped request per spoken turn.
- **Knowledge ingestion** — tenant adds/updates KnowledgeSource (URL/upload) or scheduled recrawl sweep fires.
- **Outreach send** — campaign approved/scheduled, or journey step due.
- **Production deploy (manual)** — human runs ./deploy.sh after npm run build.

## Key knowledge
- Architecture [strongly_inferred]
- Database [strongly_inferred]
- API surface [strongly_inferred]
- Historical lessons [verified]
- chat-agent-saas: overview [verified]
- Tests & commands [verified]
