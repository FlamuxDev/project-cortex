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
| 957 | 4589 | 24 | 11 | 551 | 135 | 161 | 17 | 32 (0 stale) |

## Examiner pages
- [[chat-agent-saas/API Surface|API Surface]]
- [[chat-agent-saas/Code Map|Code Map]]
- [[chat-agent-saas/Database|Database]]
- [[chat-agent-saas/Flows|Flows]]
- [[chat-agent-saas/History & Hotspots|History & Hotspots]]
- [[chat-agent-saas/Test Map|Test Map]]

## Pitfalls & rules (memories)
- Historical lessons [verified]
- Risks & technical debt [verified]

## Modules
- [[chat-agent-saas/modules/Agents-Crud-Config|agents CRUD + config]] —  [inferred]
- [[chat-agent-saas/modules/Ai-Studio-Notifications|ai-studio & notifications]] —  [inferred]
- [[chat-agent-saas/modules/Analytics-Quality-Analysis|analytics / quality analysis]] —  [inferred]
- [[chat-agent-saas/modules/Artifacts-Files-Reports|artifacts / files / reports]] —  [inferred]
- [[chat-agent-saas/modules/Auth-Session-Dashboard-Identity|auth & session (dashboard identity)]] —  [inferred]
- [[chat-agent-saas/modules/Billing-Plans-Quotas|billing / plans / quotas]] —  [inferred]
- [[chat-agent-saas/modules/Booking-Demo-Scheduler|booking (demo scheduler)]] —  [inferred]
- [[chat-agent-saas/modules/Channels-Whatsapp-Messaging-Integrations|channels / WhatsApp & messaging integrations]] —  [inferred]
- [[chat-agent-saas/modules/Chat-Conversation-Engine|chat / conversation engine]] —  [inferred]
- [[chat-agent-saas/modules/Consent-Compliance-Gdpr|consent / compliance / GDPR]] —  [inferred]
- [[chat-agent-saas/modules/External-Identity-Odoo-Sso-Into-Chat|external identity (Odoo SSO into chat)]] —  [inferred]
- [[chat-agent-saas/modules/Knowledge-Rag|knowledge / RAG]] —  [inferred]
- [[chat-agent-saas/modules/Llm-Ai-Layer|LLM / AI layer]] —  [inferred]
- [[chat-agent-saas/modules/Mcp-Model-Context-Protocol|MCP (model context protocol)]] —  [inferred]
- [[chat-agent-saas/modules/Notifications-Audit-Logs|notifications & audit logs]] —  [inferred]
- [[chat-agent-saas/modules/Odoo-Dynatrace-Splunk-Native-Enterprise-Connectors|odoo / dynatrace / splunk (native enterprise connectors)]] —  [inferred]
- [[chat-agent-saas/modules/Outreach-Campaign-Manager|outreach / Campaign Manager]] —  [inferred]
- [[chat-agent-saas/modules/Prompt-Personality-Layer|prompt & personality layer]] —  [inferred]
- [[chat-agent-saas/modules/Safety-Screening-Layer|safety screening layer]] —  [inferred]
- [[chat-agent-saas/modules/Social-Publishing-Push|social publishing & push]] —  [inferred]
- [[chat-agent-saas/modules/Tenancy-Org-Isolation|tenancy / org isolation]] —  [inferred]
- [[chat-agent-saas/modules/Transcript-Crawler-Services|transcript & crawler services]] —  [inferred]
- [[chat-agent-saas/modules/Voice-Elevenlabs|voice / ElevenLabs]] —  [inferred]
- [[chat-agent-saas/modules/Widget-Client-Embeddable-Frontend|widget client (embeddable frontend)]] —  [inferred]

## Flows
- **1) Inbound WhatsApp (v2) → reply** — 
- **2) Agent creation/config** — 
- **3) Knowledge ingestion → retrieval** — 
- **4) Booking flow** — 
- **5) Auth/login session issuance** — 
- **6) Org onboarding (register)** — 
- **7) Human handoff (discovered flow)** — user asks / `[ESCALATE_TO_HUMAN]` marker (stripped from KB chunks so RAG can't plant it, `rag.ts:24-26`) / safety verdic
- **8) Voice custom-LLM turn (branch namesake)** — 
- **9) Scheduled knowledge recrawl (discovered flow)** — 
- **10) Support inbox reply (discovered flow)** — 
- **11) Campaign send (Campaign Manager)** — 

## Key knowledge
- Architecture [strongly_inferred]
- Database [strongly_inferred]
- API surface [strongly_inferred]
- Historical lessons [verified]
- chat-agent-saas: overview [verified]
- Tests & commands [verified]
