---
cortex-generated: true
title: telvora
tags: [project]
---

# Telvora

**Path:** `/home/aboud/Dev/Telvora`  
**Kind:** monorepo | **Languages:** .go,.ts,.tsx,.sql | **Frameworks:** None

**HEAD:** `7423f040ed46` | **Brain:** `7423f040ed46` | FRESH

| Files | Symbols | Modules | Flows | APIs | DB | Tests | Decisions | Memories |
|---|---|---|---|---|---|---|---|---|
| 758 | 3467 | 13 | 7 | 402 | 104 | 197 | 8 | 21 (0 stale) |

## Modules
- [[telvora/modules/Analytics-Models-Decisions-Opportunities-Alerts|Analytics, models, decisions, opportunities, alerts]] — KPI semantic layer with A/B/C causal rigor grades; model registry/lifecycle/templates/monitoring; de [verified]
- [[telvora/modules/Campaigns-Journeys-Channels-Experiments|Campaigns, journeys, channels, experiments]] — versioned campaigns with lifecycle (draft→validating→awaiting approval→running→completed/killed) + k [verified]
- [[telvora/modules/Connectors-Ingestion-Mapping-Quality-Identity-Resolution|Connectors, ingestion, mapping, quality, identity resolution]] — get external telecom data in, map to canonical schema, quarantine bad rows, score quality, resolve d [verified]
- [[telvora/modules/Customer-360-Features|Customer 360 + features]] — unified person view (accounts/subscriptions/usage/billing/network/interactions/consent/campaign hist [verified]
- [[telvora/modules/Dsar-Retention-Ops-Console|DSAR, retention, ops console]] — DSAR export/anonymization (real anonymization, not row deletion), retention sweeps, operations snaps [verified]
- [[telvora/modules/Go-Modular-Monolith-All-Domains|Go modular monolith (all domains)]] — every REST endpoint, background worker, and domain rule for the platform [verified]
- [[telvora/modules/Governed-Agentic-Layer|Governed agentic layer]] — LLM conversations (converse), per-tenant AI policy (allowed models pinned to simulator by default),  [verified]
- [[telvora/modules/Identity-Tenancy-Rbac-Audit-Pii|Identity, tenancy, RBAC, audit, PII]] — sessions (opaque bearer tokens, SHA-256-at-rest), Argon2id passwords, TOTP MFA, invite/verify/recove [verified]
- [[telvora/modules/Next-Js-App-Marketing-Auth-Console|Next.js app (marketing + auth + console)]] — bilingual (en/ar RTL) public site, auth screens, and the full operator console (~74 routes) [verified]
- [[telvora/modules/Playwright-Suite-Aws-Cdk-Pipelines|Playwright suite + AWS CDK + pipelines]] — black-box flows against running stack (EN+AR browser locales); IaC + CI/CD [verified]
- [[telvora/modules/Python-Training-Scoring-Sidecar|Python training/scoring sidecar]] — leakage-safe windowed training (churn classification, CLV regression, propensity/NBO with productCat [verified]
- [[telvora/modules/Segments-Offers-Consent-Approvals|Segments, offers, consent, approvals]] — rule-builder segments (AST → SQL, safelisted predicates), product catalog vs CVM offers, consent/con [verified]
- [[telvora/modules/Shared-Frontend-Libraries|Shared frontend libraries]] — @telvora/ui (27 components incl. DecisionTrace, AuditLogRow, ConsentStatusPill), design-tokens (toke [inferred]

## Flows
- **Self-service signup → first Tenant Admin** — visitor submits POST /api/v1/auth/signup {organizationName, ownerEmail} (public)
- **Batch ingestion → canonical model** — POST /api/v1/tenant/integrations/{id}/batch (or pull/webhook/stream)
- **Real-time decision (NBA-NBO)** — POST /api/v1/tenant/decisions {personId, ...} (authenticated, low-latency path)
- **Model training lifecycle (Go↔Python)** — model version created (optionally from template) → submit-approval → promote → train/score via ML_SERVICE_URL
- **Governed campaign execution** — campaign start after validation + approval gate
- **Journey execution** — TriggerRun or event_trigger node match; waits resumed by 2s scheduler worker
- **LLM converse (agentic draft)** — POST /api/v1/tenant/ai/converse

## Key knowledge
- Architecture [strongly_inferred]
- Database [strongly_inferred]
- API surface [strongly_inferred]
- Historical lessons [verified]
- Telvora: overview [verified]
- Tests & commands [verified]
