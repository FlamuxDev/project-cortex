---
cortex-generated: true
title: mawid-ai
tags: [project]
---

# Mawid-AI

**Path:** `/home/aboud/Dev/Mawid-AI`  
**Kind:** monorepo | **Languages:** .ts,.tsx,.sql,.mjs | **Frameworks:** None

**HEAD:** `1019517dfd75` | **Brain:** `1019517dfd75` | FRESH

| Files | Symbols | Modules | Flows | APIs | DB | Tests | Decisions | Memories |
|---|---|---|---|---|---|---|---|---|
| 379 | 1208 | 16 | 7 | 109 | 92 | 25 | 10 | 24 (0 stale) |

## Examiner pages
- [[mawid-ai/API Surface|API Surface]]
- [[mawid-ai/Code Map|Code Map]]
- [[mawid-ai/Database|Database]]
- [[mawid-ai/Flows|Flows]]
- [[mawid-ai/History & Hotspots|History & Hotspots]]
- [[mawid-ai/Test Map|Test Map]]

## Pitfalls & rules (memories)
- Historical lessons [verified]
- Risks & technical debt [verified]

## Modules
- [[mawid-ai/modules/Booking-Engine|Booking engine]] — pure-ish business rules for availability and slot-safe writes. [inferred]
- [[mawid-ai/modules/Client-Api-Layer-Desktop-Mobile-Parity|Client API layer (desktop/mobile parity)]] — single typed client + bearer/refresh auth for desktop & Flutter clients. [inferred]
- [[mawid-ai/modules/Cloud-Api-Infrastructure|Cloud API infrastructure]] — all Graph API I/O + credential crypto + webhook verification. [inferred]
- [[mawid-ai/modules/Contract-Swagger-Ui|Contract & Swagger UI]] — machine-checked API documentation without codegen dependency. [inferred]
- [[mawid-ai/modules/Deposits-Webhooks|Deposits & webhooks]] — optional deposit checkout + webhook verification. [inferred]
- [[mawid-ai/modules/Industry-Presets|Industry presets]] — seed services/catalog per business vertical chosen at signup. [inferred]
- [[mawid-ai/modules/Lifecycle-Reminders-Outbound|Lifecycle/reminders/outbound]] — post-booking confirmations, cron reminders, template rendering, deposit gating. [inferred]
- [[mawid-ai/modules/Model-Transcription-Rag|Model, transcription, RAG]] — sole Gemini build site; voice transcription; org knowledge embeddings. [inferred]
- [[mawid-ai/modules/Multichannel-Foundation-Dormant|Multichannel foundation (dormant)]] — shared Meta webhook plumbing for Messenger/Instagram alongside WhatsApp. [inferred]
- [[mawid-ai/modules/Next-Js-Surfaces|Next.js surfaces]] — marketing site, auth pages, owner dashboard, admin, all API routes. [inferred]
- [[mawid-ai/modules/Pure-Shared-Kernel|Pure shared kernel]] — deterministic date/timezone/booking-rule logic; zero intra-repo imports (true leaf). [inferred]
- [[mawid-ai/modules/Schema-Client-Ssot|Schema + client SSOT]] — Drizzle schema (36 tables) + pooled postgres client. [inferred]
- [[mawid-ai/modules/Settings-Message-Repository|Settings + message repository]] — platform flag resolution and the centralized history-read invariant. [inferred]
- [[mawid-ai/modules/Tauri-Wrapper|Tauri wrapper]] — native window over hosted web app; deep links return OAuth/billing flows to web destinations. [inferred]
- [[mawid-ai/modules/The-Gemini-Agent|The Gemini agent]] — system prompt + tool-calling loop + the single server integrity invariant. [inferred]
- [[mawid-ai/modules/Whatsapp-Inbound-Meta-Channels|whatsapp-inbound & meta-channels]] — drive the agent from channel events; keep backend free of ai imports. [inferred]

## Flows
- **WhatsApp inbound → AI reply (the critical path)** — Meta POST /api/whatsapp/webhook (text or audio)
- **AI-driven booking** — customer asks to book inside WhatsApp thread
- **Deposit payment** — booking rule requires deposit OR dashboard action
- **Reminder cron** — external cron hits GET /api/cron/appointment-reminders (Bearer/x-cron-secret/platform_settings.cron_secret; 503 unconfig
- **Auth (web + client apps)** — login/register or client-app bootstrap
- **Deploy** — push to main
- **Desktop deep-link return** — OAuth/billing completes in system browser → mawid:// scheme

## Key knowledge
- Architecture [strongly_inferred]
- Database [strongly_inferred]
- API surface [strongly_inferred]
- Historical lessons [verified]
- mawid-ai: overview [verified]
- Tests & commands [verified]
