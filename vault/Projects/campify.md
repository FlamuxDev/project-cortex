---
cortex-generated: true
title: campify
tags: [project]
---

# Campify

**Path:** `/home/aboud/Dev/Campify`  
**Kind:** monorepo | **Languages:** .ts,.sql,.tsx,.mjs | **Frameworks:** None

**HEAD:** `ad245fa6ef3d` | **Brain:** `ad245fa6ef3d` | FRESH

| Files | Symbols | Modules | Flows | APIs | DB | Tests | Decisions | Memories |
|---|---|---|---|---|---|---|---|---|
| 298 | 1347 | 20 | 8 | 73 | 109 | 71 | 14 | 28 (0 stale) |

## Modules
- [[campify/modules/Ast-Compiled-To-Parameterised-Sql|AST compiled to parameterised SQL]] — dynamic/static audiences defined as JSON AST, compiled live with bind params only. [verified]
- [[campify/modules/Campaign-Domain-State-Machine-Audience-Approval|campaign domain, state machine, audience, approval]] — lifecycle draft→in_review→scheduled→running… with version-bound four-eyes approval. [verified]
- [[campify/modules/Commercial-Limits|commercial limits]] — plan catalog + per-workspace overrides; atomic quota reservation for billed metrics. [verified]
- [[campify/modules/Contact-Profiles-Fields-Tags-Lists|contact profiles, fields, tags, lists]] — canonical person record + custom fields/tags/lists, normalization of emails/phones. [verified]
- [[campify/modules/Csv-Xlsx-Dry-Run-Then-Commit|CSV/XLSX dry-run then commit]] — two-phase import: parse/validate/dedupe into a persisted plan, preview it, then apply. [verified]
- [[campify/modules/Delivery-Engine-Process|delivery engine process]] — all outbound side effects owned here; five polls per 5s tick. [verified]
- [[campify/modules/Events-Conversions-Attribution-Roi-Reports|events, conversions, attribution, ROI, reports]] — API-key event ingestion, last-touch attribution, per-campaign reports + dashboard rollups. [verified]
- [[campify/modules/Follow-Up-Queue|follow-up queue]] — tasks handed from campaigns/journeys to humans, assigned, tracked to outcome. [strongly_inferred]
- [[campify/modules/Http-Plumbing-Fastify|HTTP plumbing (Fastify)]] — everything cross-cutting on the API: zod boundaries, error mapping, correlation ids, throttles, guar [verified]
- [[campify/modules/Ledger-Suppression-Send-Gate|ledger, suppression, send gate]] — strict opt-in consent ledger + suppression list; THE gate every send passes. [verified]
- [[campify/modules/Native-Companies-Deals-Pipeline|native companies/deals/pipeline]] — native CRM (ADR-0013): companies, deals on per-workspace pipelines, activity timeline. [strongly_inferred]
- [[campify/modules/Next-Js-Ui-Bff|Next.js UI + BFF]] — public site, private app UI, server actions, i18n ar/en RTL. [verified]
- [[campify/modules/Outbound-Subscriptions-Inbound-Provider-Events|outbound subscriptions + inbound provider events]] — signed outbound event delivery to customer URLs; HMAC-verified inbound Resend events. [verified]
- [[campify/modules/Provider-Implementations-Behind-Ports|provider implementations behind ports]] — fake (zero network), queue-inprocess (Postgres-as-queue), email-resend, ai-gemini, webhook-http. [verified]
- [[campify/modules/Schema-Rls-Policies-Tenant-Data-Access|schema, RLS policies, tenant data access]] — migrations, RLS policies, and the `withTenant` boundary around every tenant query. [verified]
- [[campify/modules/Send-Pipeline-Retries-Quiet-Hours-Provider-Events|send pipeline, retries, quiet hours, provider events]] — turn a claimed message into a real send through every §13.3 control; ingest provider status. [verified]
- [[campify/modules/Studio-Versions-Templates-A-B-Ai-Copilot-Personalization|studio, versions, templates, A/B, AI copilot, personalization]] — channel content per campaign version; immutable append-only versions; variant allocation; AI suggest [verified]
- [[campify/modules/Users-Sessions-Workspaces-Rbac|users, sessions, workspaces, RBAC]] — signup/verify/login/logout, sessions, memberships, invitations, the RBAC matrix. [verified]
- [[campify/modules/Validated-Environment|validated environment]] — the ONLY reader of process.env; zod-validated, fails boot loudly. [verified]
- [[campify/modules/Visual-Automation-Engine|visual automation engine]] — publishable node graphs (wait/send/task/branch/webhook) with enrollment and step execution. [verified]

## Flows
- **signup-verify-workspace-invite (CUJ-1)** — POST /v1/auth/signup (or web form → /api/signup proxy)
- **csv-import (CUJ-2)** — upload in /app/contacts/import
- **consent-to-send (CUJ-3)** — POST …/consent or suppression, then any send attempt
- **segment-build-and-snapshot (CUJ-4)** — /app/segments builder
- **campaign-launch (CUJ-5)** — builder tabs → submit
- **journey-execution (CUJ-6)** — publish journey
- **engagement-attribution (CUJ-7)** — provider webhook or partner POST …/events
- **outbound-webhook-delivery** — any of 8 domain events with active subscription

## Key knowledge
- Architecture [strongly_inferred]
- Database [strongly_inferred]
- API surface [strongly_inferred]
- Historical lessons [verified]
- Campify: overview [verified]
- Tests & commands [verified]
