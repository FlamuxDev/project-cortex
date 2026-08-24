---
cortex-generated: true
title: mushagil
tags: [project]
---

# Mushagil

**Path:** `/home/aboud/Dev/Mushagil`  
**Kind:** monorepo | **Languages:** .ts,.tsx,.mjs,.sql | **Frameworks:** None

**HEAD:** `2725504c477f` | **Brain:** `2725504c477f` | FRESH

| Files | Symbols | Modules | Flows | APIs | DB | Tests | Decisions | Memories |
|---|---|---|---|---|---|---|---|---|
| 598 | 2412 | 11 | 9 | 254 | 97 | 132 | 13 | 19 (0 stale) |

## Modules
- [[mushagil/modules/Background-Worker-Process|Background Worker Process]] — outbox relay, event consumers, scheduled sweeps, DLQ visibility, health endpoints. [verified]
- [[mushagil/modules/Business-Setup-Catalog-Capacity-M03-Uncommitted-Working-Tree|Business Setup, Catalog & Capacity (M03, uncommitted working tree)]] — deterministic Beauty business truth — profile, locations/hours/closures, booking policy, knowledge,  [inferred]
- [[mushagil/modules/Cross-Cutting-Ux-Infrastructure|Cross-Cutting UX Infrastructure]] — structured logging w/ redaction; ar/en catalogs + formatting; accessible RTL-safe UI primitives. [verified]
- [[mushagil/modules/Fail-Closed-Configuration-Provider-Modes|Fail-Closed Configuration & Provider Modes]] — validated env schema + secret handling + production fake/sandbox refusal. [verified]
- [[mushagil/modules/Generated-Api-Contract-Client|Generated API Contract & Client]] — committed openapi.json + generated types/client; drift gate. [verified]
- [[mushagil/modules/Identity-Tenancy-Rbac-Trial-Paypal-Billing-M02|Identity, Tenancy, RBAC, Trial & PayPal Billing (M02)]] — OIDC login/sessions, tenants/memberships/invitations, central permission evaluation, 14-day trial, P [verified]
- [[mushagil/modules/Industry-Pack-Contract-M03-Uncommitted-Working-Tree|Industry Pack Contract (M03, uncommitted working tree)]] — declarative versioned pack definitions (BEAUTY v1/v2 seeded), custom fields, install/migrate/rollbac [inferred]
- [[mushagil/modules/Next-Js-Web-Application|Next.js Web Application]] — bilingual (ar default) operator console consuming generated API client. [verified]
- [[mushagil/modules/Platform-Foundation-Kernel|Platform Foundation Kernel]] — IDs/time/money/errors/correlation + unit-of-work, idempotency, outbox relay, queue wrapper, tenant f [verified]
- [[mushagil/modules/Postgres-Schema-Roles-Migration-Harness|Postgres Schema, Roles & Migration Harness]] — authoritative schema (platform + business schemas), DB roles, checksummed forward-only migrations. [verified]
- [[mushagil/modules/Test-Suites-Verification-Gates|Test Suites & Verification Gates]] — suite registry routing, ephemeral DB harness, anti-cheating guards. [verified]

## Flows
- **Tenant Request (every authenticated API call)** — any /v1/* request with session cookie
- **Login (OIDC + PKCE)** — user clicks login
- **Tenant Creation & Trial Start** — authenticated user creates workspace
- **Subscription Verification (PayPal)** — subscriber completes PayPal approval; frontend posts subscription id
- **PayPal Webhook Intake** — PayPal POSTs /v1/billing/paypal/webhook
- **Outbox Delivery** — committed transaction wrote outbox_event
- **Draft→Publish Business Truth (M03)** — owner finishes editing business profile/services/hours and calls publish
- **Weekly Hours Authoring** — operator sets split/overnight opening hours or staff schedule
- **Trial Expiry Sweep** — BullMQ repeatable job hourly

## Key knowledge
- Architecture [strongly_inferred]
- Database [strongly_inferred]
- API surface [strongly_inferred]
- Historical lessons [verified]
- Mushagil: overview [verified]
- Tests & commands [verified]
