---
cortex-generated: true
title: cvm
tags: [project]
---

# CVM

**Path:** `/home/aboud/Dev/CVM`  
**Kind:** monorepo | **Languages:** .ts,.tsx,.sql,.py | **Frameworks:** None

**HEAD:** `2d7ffcee167d` | **Brain:** `2d7ffcee167d` | FRESH

| Files | Symbols | Modules | Flows | APIs | DB | Tests | Decisions | Memories |
|---|---|---|---|---|---|---|---|---|
| 432 | 2761 | 24 | 8 | 539 | 298 | 50 | 13 | 32 (0 stale) |

## Modules
- [[cvm/modules/A-B-Experiments-Outcomes|A/B experiments & outcomes]] — deterministic sticky bucketing, control declared first, held-out customers still measured; variants, [strongly_inferred]
- [[cvm/modules/Analytics-Kpis|analytics & KPIs]] — executive KPIs computed at read time; cohorts, behaviour funnels, trends, affinity, segment overlap, [strongly_inferred]
- [[cvm/modules/Append-Only-Audit-Trail|append-only audit trail]] — audit_event append-only at DB level; searchable; correlation-joined; /audit/correlation/{id} shows e [verified]
- [[cvm/modules/Audiences-Rule-Language|audiences & rule language]] — one versioned JSON rule AST (ADR-012) validated against closed per-tenant field catalogue, compiled  [verified]
- [[cvm/modules/Campaign-Orchestration|campaign orchestration]] — campaigns with fourteen §12 fields, immutable versions, ten pre-launch checks, separation-of-duties  [verified]
- [[cvm/modules/Consent-Contact-Policy|consent & contact policy]] — append-only consent records, suppression entries, do-not-contact, quiet hours in customer timezone,  [strongly_inferred]
- [[cvm/modules/Customer-360-Projection|Customer 360 projection]] — materialised per-customer profile (not a view), timeline, PII masking, gated+audited export. [verified]
- [[cvm/modules/Cvm-Platform-Infrastructure-Kernel|@cvm/platform infrastructure kernel]] — config/context/contracts/crypto/db/events/http/jobs/storage/telemetry; imported by everyone, imports [verified]
- [[cvm/modules/Decision-Engine-Gate-Ranker|decision engine (gate + ranker)]] — PRD §21 eleven-step NBA: candidates from catalog → eligibility/policy BEFORE ranking → pure ranker o [verified]
- [[cvm/modules/Erasure-Governance|erasure & governance]] — right-to-erasure requests (approval-gated, irreversible): personal data removed, audit trail intact, [strongly_inferred]
- [[cvm/modules/Execution-Engine-Channels|execution engine & channels]] — effectively-once send execution (ADR-010): claim row in delivery_attempt unique (tenant_id, dedupe_k [verified]
- [[cvm/modules/Fastify-Http-Api|Fastify HTTP API]] — serve the versioned REST contract; composition root wiring platform ports to module implementations. [verified]
- [[cvm/modules/Feature-Platform|feature platform]] — declarative feature definitions compiled to SQL (definitions ARE data — ADR-017), versioned; freshne [strongly_inferred]
- [[cvm/modules/Fixtures-Ops-Drills-Offline-Ml|fixtures, ops drills, offline ML]] — datagen (deliberately dirty synthetic telco dataset — 53k customers/3.38M events fixture), seed (dev [verified]
- [[cvm/modules/Identity-Access-Management|Identity & Access Management]] — users, roles/personas, permissions (30 domain perms, 10 persona roles), sessions (opaque, server-sid [strongly_inferred]
- [[cvm/modules/Identity-Resolution-Merge|identity resolution & merge]] — deterministic cross-source resolution into canonical customers; ambiguous cases raise identity_confl [verified]
- [[cvm/modules/Ingestion-Contracts-Quarantine-Quality|ingestion, contracts, quarantine, quality]] — data sources/contracts, batch file ingest, eight §7.3 quality detections, quarantine with reasons +  [verified]
- [[cvm/modules/Model-Registry-Scoring-Platform-Side-Of-Track-B|model registry & scoring (platform side of Track B)]] — governed model objects (ADR-009): model/version/deployment/metric/drift_check/challenger/shadow_scor [verified]
- [[cvm/modules/Next-Js-Operator-Console|Next.js operator console]] — bilingual (en/ar RTL) permission-gated console; 100% RSC, zero client interface JS. [verified]
- [[cvm/modules/Offer-Catalog|offer catalog]] — offers with sixteen §11 fields, immutable versions, separation-of-duties approval, transactional cap [strongly_inferred]
- [[cvm/modules/Outbox-Relay-Housekeeping|outbox relay & housekeeping]] — outbox_message relay to subscribers (outbox.relay cron), retention enforcement, partition creation v [strongly_inferred]
- [[cvm/modules/P8-P9-Surface|P8/P9 surface]] — trigger_rule evaluation (realtime dispatch listener in worker + batch fallback), journey builder/ver [inferred]
- [[cvm/modules/Pg-Boss-Job-Consumer|pg-boss job consumer]] — execute all background work; never serves requests. [verified]
- [[cvm/modules/Recurring-Job-Registrar-Singleton|recurring-job registrar (singleton)]] — evaluate pg-boss cron and enqueue recurring jobs; enqueues, never executes. [verified]

## Flows
- **Ingestion → quarantine → replay** — POST /v1/ingest/{source_code} batch upload or scheduled connector pull
- **Identity resolve → merge/unmerge → C360 reprojection** — ingestion of identifiers; manual conflict resolution; POST /v1/identity/merge|unmerge
- **Audience build → materialise → explain** — UI rule builder (AST in URL) → POST /v1/segments; schedule
- **Offer approve → decision (gate+rank) → NO_ACTION possible** — POST /v1/decisions (or /batch ≤500)
- **Campaign approve → run → deliver (effectively-once) → receipts → funnel** — campaign launch (requires approval + typed confirm)
- **§39 end-to-end trace** — GET /v1/trace/{deliveryId}; console /trace/[id]
- **Governed ML lifecycle (Track B)** — pnpm ml:load-fixture → refresh-features → train; then API approve/deploy
- **Right to erasure** — POST /v1/erasure-requests → approval

## Key knowledge
- Architecture [strongly_inferred]
- Database [strongly_inferred]
- API surface [strongly_inferred]
- Historical lessons [verified]
- CVM: overview [verified]
- Tests & commands [verified]
