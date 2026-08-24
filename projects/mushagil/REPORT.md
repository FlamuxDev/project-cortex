# CORTEX REPORT — Mushagil

## META
project_id: mushagil
root: /home/aboud/Dev/Mushagil
kind: pnpm + Turborepo strict TypeScript monorepo (modular monolith, 3 runtime processes)
languages: TypeScript (strict, Node >=26), SQL (PostgreSQL migrations), CSS Modules
frameworks: Next.js App Router (web), NestJS 11 + Fastify (api), standalone worker (BullMQ), Drizzle (partial mappings) + raw parameterized SQL, zod (env), class-validator (DTOs), Radix UI wrapped by @mushagil/ui, pino/OpenTelemetry (observability)
package_managers: pnpm@9.15.4 (+ Turborepo 2.10.11 task runner)
test_frameworks: Vitest 4.1.11 (all suites), Playwright chromium (e2e), suite router scripts/run-suite.mjs over quality/suite-registry.json
deployment: local docker-compose (postgres:18 on 127.0.0.1:55533, redis:8 on 127.0.0.1:56480); GitHub Actions CI (.github/workflows/ci.yml runs all gates incl. e2e/a11y); infra/environments/{local,staging,production} are README skeletons only — no real cloud deploy exists yet [inferred from empty infra dirs]

## OVERVIEW

Mushagil is an Arabic-first, WhatsApp-first "AI employee" operating system for Saudi service businesses (first vertical: beauty salons). A governed Gemini AI receptionist will handle customer WhatsApp conversations and owner commands, while deterministic systems protect business truth, bookings, permissions, money, and consent. Core loop: Inquiry → Qualification → Booking → Service Delivery → Payment Record → Follow-up → Rebooking (`PRODUCT.md` §1). The AI is explicitly not a source of business truth (`PRODUCT.md` §7).

Users are Saudi SMB owner/operators and their staff (Owner/Admin/Manager/Receptionist/Staff roles), reached via a bilingual Arabic-default web app; end customers interact primarily through WhatsApp (planned M06/M07, not yet implemented). SaaS billing is PayPal Subscriptions (STARTER $79 / GROWTH $129 / PRO $199 / BUSINESS contact-sales) with a Mushagil-owned 14-day trial that needs no PayPal at start (`PRODUCT.md` §8).

Deployment today is development-only: `pnpm bootstrap` boots docker-compose Postgres+Redis, three processes run locally (web :3002, api :3000, worker health :3001). Production/staging infra directories exist as README placeholders; live Auth0/PayPal activation items are explicitly pending with production configured to fail closed (`MODULES.md` M02 evidence; docs/project/CURRENT_STATE.md).

Delivery is contract-driven: root `MODULES.md` is both the engineering contract (23 numbered sections: RLS, authz, transactions/outbox/idempotency, state machines, API envelope, provider boundaries, i18n/a11y, anti-cheating rules) and the ordered module queue M01–M16. Status: M01 (platform foundation + delivery spine) DONE, M02 (identity/tenancy/authz/trial/billing) DONE, M03 (business setup/pack core/catalog/capacity) IN_PROGRESS — its code exists in the working tree but is uncommitted (~136 dirty files; docs/project/CURRENT_STATE.md still says NOT_STARTED, verified against HEAD 638838a). [inferred] The repo appears to be built by AI orchestrator + implementer sessions ("orchestrator" language throughout MODULES.md evidence blocks, deleted CLAUDE.md build protocol at HEAD).

## ARCHITECTURE

Runtime shape (docs/project/SYSTEM_MAP.md, verified in source):

```
Browser → apps/web (Next.js App Router, locale-aware ar/en)
        → apps/api (NestJS on Fastify, /v1 REST + /internal/v1 + raw PayPal webhook route)
             → module application/domain packages
             → PostgreSQL transaction: SET app.tenant_id → RLS → mutation + audit_event + outbox_event → commit
        → apps/worker: outbox relay poll (250ms) → BullMQ → consumers w/ processed_event dedupe;
                       hourly trial-expiry repeatable job; health server :3001; DLQ metric
```

- **Authoritative state**: PostgreSQL 18 only. Redis/BullMQ transports jobs, never business truth ("queue success is not business success", MODULES.md §4).
- **Transaction pattern**: validate → authorize (central PermissionEvaluator) → one UoW transaction (mutation + immutable audit event + outbox event) → commit → async external effect. Provider/network calls inside an open transaction are structurally blocked by an AsyncLocalStorage guard (`packages/platform/src/domain/transaction-guard/guard.ts` — `guardProviderCall` wraps adapters).
- **Tenant isolation**: every tenant table has forced RLS + matching USING/WITH CHECK policy; tenant context set per-transaction via `platform.current_tenant_id()`; child rows use composite `(parent_id, tenant_id)` FK against parent `unique(id, tenant_id)` so cross-tenant children are structurally impossible (ADR 0003; migration 0004).
- **DB role separation**: `mushagil_owner` (superuser, DDL/migrations/tests), `mushagil_app` (runtime, NOBYPASSRLS), `mushagil_relay` (BYPASSRLS but granted exactly outbox_event SELECT/UPDATE, processed_event + probe_projection SELECT/INSERT), `mushagil_identity` (cross-tenant session resolution) — `infra/postgres-init/01-create-app-role.sql`, migrations 0002/0003.
- **Provider boundary**: registry of providers {auth0, meta-whatsapp, gemini, paypal, objectStorage} × modes {live,sandbox,fake}; production refuses fake always and sandbox unless allow-listed (`packages/config/src/provider-mode.ts`). Adapters: fake+live identity provider, sandbox+live PayPal client (`packages/modules/identity-tenant-billing/src/infrastructure/`); Meta WhatsApp/Gemini not yet built.
- **Contracts**: committed OpenAPI generated from Nest decorators (`apps/api/src/openapi/generate-openapi.ts`), typed client via openapi-typescript/openapi-fetch (`packages/contracts/src/generated/api.d.ts`); `pnpm verify:openapi` fails on drift.
- **Boundary enforcement**: `.dependency-cruiser.cjs` rules — domain layers cannot import pg/ioredis/bullmq/pino/otel/database/observability; cross-package imports only via package index; web feature code cannot import @radix-ui directly; no circular deps. `eslint.config.js` complements.
- **Background jobs**: BullMQ queues `mushagil-platform-events` (outbox dispatch; namespaced prefix from config) and `mushagil-trial-expiry` (hourly repeatable sweep) — `apps/worker/src/outbox-worker.ts`, `apps/worker/src/trial-expiry-worker.ts`. Retries exponential (5 attempts / 3 attempts), DLQ metric registered.
- **External integrations present**: Auth0-compatible OIDC (fake tested, live implemented), PayPal Subscriptions API (sandbox+live clients), webhook verification. Planned: Meta WhatsApp Cloud API (M06), Google Gemini adapter (M07) — env vars reserved in `.env.example`, no code yet.

Working-tree caveat: ARCHITECTURE.md, CLAUDE.md, QUALITY.md were deleted (staged) and their authority folded into MODULES.md's engineering contract; many code comments still cite "ARCHITECTURE decision #N" / "ARCHITECTURE §9" (e.g. `subscription-state.ts:3`, main.ts comments) — stale references to files no longer in the tree.

## MODULES

### platform-core — Platform Foundation Kernel
purpose: IDs/time/money/errors/correlation + unit-of-work, idempotency, outbox relay, queue wrapper, tenant fairness, provider-call guard.
path_prefixes: packages/platform/src
key_files: src/application/unit-of-work/unit-of-work.ts, src/infrastructure/unit-of-work/pg-transaction-runner.ts, src/infrastructure/outbox/outbox-relay.ts, src/infrastructure/outbox/bullmq-outbox-publisher.ts, src/infrastructure/queue/{queue-wrapper,processed-event-guard,scheduler}.ts, src/domain/errors/app-error.ts, src/domain/money/money.ts, src/domain/ids/id.ts (UUIDv7), src/domain/correlation/context.ts, src/domain/transaction-guard/guard.ts, src/domain/queue/tenant-fairness.ts
entrypoints: imported by every app/module; OutboxRelay driven by apps/worker/src/outbox-worker.ts
responsibilities: one canonical mutation pattern (mutate+audit+outbox in a single tx); exactly-once logical effects via processed_event ledger; idempotency keyed tenant+principal+operation+idempotency key+canonical request hash (src/domain/idempotency/canonical-hash.ts).
invariants: audit/outbox failure rolls back the domain mutation (proven tests/integration unit-of-work-atomicity.test.ts); FOR UPDATE SKIP LOCKED relay claim — 3 concurrent relays publish each event once (M01 evidence); provider calls forbidden while tx open.
pitfalls: QueueWrapper must duplicate() the Redis connection for the blocking worker (a shared connection once caused a consumer wake-up hang misattributed to the queue name — comment at apps/worker/src/outbox-worker.ts:14–20 documents this).
confidence: verified

### config-env — Fail-Closed Configuration & Provider Modes
purpose: validated env schema + secret handling + production fake/sandbox refusal.
path_prefixes: packages/config/src
key_files: src/env-schema.ts, src/config.ts, src/provider-mode.ts, src/secret.ts, src/load-env-file.ts
entrypoints: getConfig() called at boot of api/worker
responsibilities: single zod schema for all MUSHAGIL_*/DATABASE_*/REDIS_* vars; Secret type prevents accidental leakage; load order .env.example → .env.test.local → process env.
invariants: assertProviderModesAllowed throws PROVIDER_MODE_FORBIDDEN in production for fake mode or un-allow-listed sandbox mode.
pitfalls: defaults for all five provider modes are "fake" — safe locally, fatal in prod by design; REDIS_SOCKET_PATH unix-socket path is a sandbox-only alternative to TCP (portability trap documented in .env.example).
confidence: verified

### database-migrations — Postgres Schema, Roles & Migration Harness
purpose: authoritative schema (platform + business schemas), DB roles, checksummed forward-only migrations.
path_prefixes: packages/database/migrations, packages/database/src
key_files: migrations/0001_platform_foundation.sql … 0004_business_setup_catalog_capacity.sql (1405 lines, 29 business tables), src/pools.ts (app/identity/relay/admin/test pools), src/migration-runner/{runner,checksum,discover,cli}.ts, src/schema/*.ts (Drizzle mappings)
entrypoints: `pnpm db:migrate|db:status|db:recreate`; runner CLI src/migration-runner/cli.ts
responsibilities: migration checksums + locks; recreate guard test prevents wiping non-local DBs.
invariants: RLS enabled AND forced on every tenant table across APP_SCHEMAS=["platform","business"] except exactly platform.schema_migration and platform.app_user (tests/migrations/rls-invariant.test.ts, generalized per ADR 0003); mushagil_relay grant scope asserted minimal (tests/security/relay-role-least-privilege.test.ts).
pitfalls: history is never rewritten — M01's deferred tenant FKs were closed later via NOT VALID + VALIDATE (0003, M02 evidence "fk debt"); new schema ⇒ must deliberately add to APP_SCHEMAS or its tables silently escape the invariant.
confidence: verified

### contracts-openapi — Generated API Contract & Client
purpose: committed openapi.json + generated types/client; drift gate.
path_prefixes: packages/contracts, apps/api/src/openapi
key_files: openapi/openapi.json, src/generated/api.d.ts, apps/api/src/openapi/generate-openapi.ts, scripts/verify-openapi.mjs
entrypoints: web imports createAuthenticatedApiClient types; verify gate in CI.
responsibilities: single source of HTTP truth; tamper-tested drift gate (mutating openapi.json fails exit 1, M01 evidence).
invariants: live app must match committed document exactly.
pitfalls: regeneration is part of bootstrap; forgetting to regenerate after adding routes fails verify:openapi (intentionally).
confidence: verified

### observability-i18n-ui — Cross-Cutting UX Infrastructure
purpose: structured logging w/ redaction; ar/en catalogs + formatting; accessible RTL-safe UI primitives.
path_prefixes: packages/observability, packages/i18n, packages/ui
key_files: observability/src (pino logger, redaction); i18n/src/catalogs/ar.ts (source of truth) + en.ts, i18n/src/format; ui/src/primitives/* (19 primitives incl. new Tabs/Textarea/TimeField), ui/src/tokens, ui/src/lint
entrypoints: getLogger(); catalog/format helpers; primitive components consumed by apps/web
responsibilities: secret/log redaction; Arabic-first catalogs with numbers/dates/money formatting helpers; logical-CSS primitives (no left/right).
invariants: Arabic catalog is key source of truth; feature code may not import Radix directly (dependency-cruiser rule).
pitfalls: edge middleware (apps/web/middleware.ts) carries an inline fallback because @mushagil/i18n may be unbuilt during dev — transient-state workaround noted in file header.
confidence: verified

### identity-tenant-billing — Identity, Tenancy, RBAC, Trial & PayPal Billing (M02)
purpose: OIDC login/sessions, tenants/memberships/invitations, central permission evaluation, 14-day trial, PayPal subscription verification/webhooks, entitlement projection.
path_prefixes: packages/modules/identity-tenant-billing, apps/api/src/identity, apps/web components LoginScreen/TeamScreen/BillingScreen/SecurityScreen/AcceptInvitationScreen/WorkspaceSwitcher
key_files: src/domain/permission-evaluator.ts (manifest-driven, deny-by-default, 9-step order), src/domain/roles.ts (grant ceiling), src/domain/subscription-state.ts, src/application/{tenant,membership,session,user,team-query,paypal-verification,billing-webhook,trial-expiry,entitlement}-service.ts, src/infrastructure/auth0/{fake,live}-identity-provider.ts, src/infrastructure/paypal/{sandbox,live}-paypal-client.ts; controllers auth/billing/members/sessions/tenants.controller.ts
entrypoints: POST /v1/auth/login → GET /v1/auth/callback (PKCE S256 + state/nonce cookies) → session cookie; POST /v1/tenants, /v1/tenants/:id/switch, /v1/invitations/accept, /v1/billing/subscriptions/verify; raw POST /v1/billing/paypal/webhook (Fastify raw-body plugin scoped to this route only — apps/api/src/main.ts:100–140)
responsibilities: resolvePrincipal re-reads membership from DB every request (immediate revocation, no poisonable role cache); last-owner invariant enforced by DB trigger + SELECT…FOR UPDATE; webhook dedupe on provider_event_id with out-of-order regression protection.
invariants: browser approval alone grants nothing — verification requires planId AND productId AND currency AND amount AND provider status AND custom_id tenant binding (paypal-verification-service.ts, six rules); APPROVAL_PENDING/APPROVED map to null (no state change); terminal CANCELED/EXPIRED never transition; downgrade/suspend never deletes data; unknown events persisted without error; PAYPAL_WEBHOOK_ID absent ⇒ production rejects every webhook (fail-closed).
pitfalls: legacy plan P-83S97234B32877119NKFP42Y has identical price but wrong product — a named mandatory test refuses it; "price parity is not authorisation" (M02 evidence). Known documented gap: genuinely lost response on tenant-create/invitation-accept returns error instead of replaying original result. Trial previews GROWTH entitlement tier (config-driven).
confidence: verified

### business-capacity — Business Setup, Catalog & Capacity (M03, uncommitted working tree)
purpose: deterministic Beauty business truth — profile, locations/hours/closures, booking policy, knowledge, onboarding, publish/readiness, services/versions/pricing, skills, staff/schedules/time-off, resources/blocks, offering resolution.
path_prefixes: packages/modules/business-capacity, apps/api/src/business, apps/api/src/catalog, packages/database/src/schema/business.schema.ts + catalog.schema.ts, apps/web components BusinessProfileScreen/LocationsScreen/KnowledgeScreen/PoliciesScreen/ServicesScreen/StaffScreen/ResourcesScreen/ReadinessScreen/OnboardingScreen/IndustryScreen
key_files: src/application/publication-service.ts (builds whole-truth JSONB snapshot + hash), src/application/published-truth-service.ts (reads ONLY business_publication — ADR 0004), src/application/offering-resolution-service.ts (deterministic price/duration/intake/staff/resource resolution against published truth), src/application/readiness-service.ts, src/domain/{pricing,duration,intake,capacity,eligibility,opening-hours,week-time,state-machines,knowledge-truth,impact,readiness}.ts, src/infrastructure/keyset-pagination.ts
entrypoints: ~50 REST routes under /v1/business/** (profile, readiness, publish, publications, knowledge, locations+hours+closures, packs install/migrate/rollback, policies draft/publish, onboarding advance/complete) and /v1/catalog/** (services, offerings/resolve, skills, staff incl. schedule/time-off, resources incl. capacity/blocks/archive-impact) — see APIS table
responsibilities: draft→publish lifecycle where publishing writes an append-only self-contained business_publication JSONB document (canonical hash + readiness evaluation) and refuses while any BLOCKING readiness item exists; per-aggregate versioning (service_version, booking_policy, knowledge_entry) referenced by publication.
invariants: availability/resolution reads published snapshots only — drafts can never leak to customers/AI; optimistic versioning with If-Match required on updates (apps/api/src/business/shared/if-match.ts returns 422 when missing); overlap-free weekly hours enforced by GiST exclusion constraints on derived int4range week-minute segments [0,10080), overnight written as two segments (ADR 0005); absolute intervals use tstzrange exclusion constraints, time-off partial on status='APPROVED'; quote-required pricing never fabricates fixed price; archive/capacity-reduction return impact previews.
pitfalls: day_of_week is ISO order 0=Monday…6=Sunday, NOT JS getDay() (ADR 0005); segments are derived state replaced wholesale with their parent rule, never edited in place; effectivity-dated schedules deliberately not modelled (would break single-exclusion guarantee); raw parameterized SQL used in infrastructure/raw-tenant-read.ts rather than full Drizzle coverage — cross-schema joins possible in principle, review must keep enforcing module boundaries (ADR 0003 consequences).
confidence: verified (code+tests read directly; module not yet marked DONE in MODULES.md)

### packs-core — Industry Pack Contract (M03, uncommitted working tree)
purpose: declarative versioned pack definitions (BEAUTY v1/v2 seeded), custom fields, install/migrate/rollback with hash pinning.
path_prefixes: packages/modules/packs
key_files: src/domain/pack-definition.ts (typed contract; parsePackDefinition is sole jsonb→typed gateway), src/domain/pack-hash.ts, src/domain/pack-migration-plan.ts, src/application/pack-installation-service.ts, src/infrastructure/pack-definition-repository.ts
entrypoints: /v1/business/packs routes (available/install/customizations/migrate/rollback/migrations)
responsibilities: packs configure terminology/custom fields/defaults without forking core; custom fields referenced by published truth are retained read-only rather than deleted (ADR 0004 consequence).
invariants: pack definition hash pinned at install; migration dry-run + rollback preserving published truth.
pitfalls: nothing may assume a jsonb `definition` value is well-formed without parsePackDefinition.
confidence: strongly_inferred (read directly, fewer dedicated tests than business-capacity)

### web-shell — Next.js Web Application
purpose: bilingual (ar default) operator console consuming generated API client.
path_prefixes: apps/web
key_files: middleware.ts (locale redirect + dev-tenant cookie), app/[locale]/layout.tsx (root layout; no bare-root layout), lib/api-client.ts (createAuthenticatedApiClient), lib/server-tenant-context.ts, lib/error-messages.ts, lib/navigation.ts, lib/readiness-blockers.ts, components/AppShell/*
entrypoints: pages under app/[locale]: login, invitations/accept, workspaces, settings/{team,security,billing,platform-probes,business/*}, services, staff, onboarding
responsibilities: permission-safe navigation, all UI states incl. offline/error (NETWORK_UNAVAILABLE retryable pattern from M01 review), no optimistic success on committing actions.
invariants: Arabic RTL structural base; dev-tenant cookie never read in production (lib/server-tenant-context.ts refuses); RSC prefetch requests must not mint a second dev tenant id (middleware comment — real tenant-consistency bug they hit).
pitfalls: dev tenant cookie flow is M01 scaffolding predating real identity; two independent cookie mechanisms (dev-tenant vs session) coexist.
confidence: verified

### worker-runtime — Background Worker Process
purpose: outbox relay, event consumers, scheduled sweeps, DLQ visibility, health endpoints.
path_prefixes: apps/worker
key_files: src/main.ts, src/outbox-worker.ts, src/trial-expiry-worker.ts, src/consumers/probe-created.consumer.ts, src/health-server.ts, src/dlq-metric.ts
entrypoints: bootstrapWorker() from src/main.ts; WORKER_HEALTH_PORT 3001 (/health/live, /health/ready)
responsibilities: EVENT_HANDLERS registry maps eventType→consumer; unknown event types logged and dropped safely; hourly trial sweep bounds EXPIRED staleness (<1 day) since BullMQ scheduler is skip-to-next (no replay backlog after outage).
invariants: graceful SIGTERM drain; relay uses mushagil_relay pool only.
pitfalls: only one real consumer exists (probe.created) — most outbox events currently have no consumer (by design until owning modules land).
confidence: verified

### testing-harness — Test Suites & Verification Gates
purpose: suite registry routing, ephemeral DB harness, anti-cheating guards.
path_prefixes: packages/testing, quality/, scripts/
key_files: quality/suite-registry.json (14 suites w/ requiredFrom module gating), scripts/run-suite.mjs (SUITE_EMPTY if a DONE-module suite matches zero files — tamper-tested), scripts/verify-suites.mjs, packages/database/tests/support/ephemeral-db.ts, vitest.config.ts (single root config)
entrypoints: pnpm test:* / verify:* root commands (package.json)
responsibilities: suites become mandatory only when their owning module is DONE in MODULES.md; unit=no DB/network, integration=real ephemeral Postgres+Redis.
invariants: MODULES.md §20 anti-cheat: weakening assertions/skipping tests/fake success invalidates green.
confidence: verified

## FLOWS

### Tenant Request (every authenticated API call)
trigger: any /v1/* request with session cookie
steps:
1. CorrelationMiddleware assigns correlationId (AsyncLocalStorage context).
2. TenantContextMiddleware parses session cookie → composite tenant resolver: production uses trusted application session/workspace; explicit dev-header path exists but is refused in production (test dev-tenant-header-refused-in-production.test.ts).
3. Principal resolved by re-reading membership/auth_session from DB (revocation immediate).
4. DTO ValidationPipe (whitelist + forbidNonWhitelisted → VALIDATION_FAILED).
5. Controller calls PermissionEvaluator.assert(resource.action, ctx) — deny-by-default manifest.
6. Application service opens UnitOfWork tx: SET app.tenant_id → RLS USING/WITH CHECK → mutate + audit_event + outbox_event → commit (provider calls blocked inside).
7. Envelope interceptor returns {data, meta:{correlationId, freshnessAt}}; AppExceptionFilter maps AppError→safe envelope (never stack/SQL/provider payload).
files: apps/api/src/common/{correlation,tenant,envelope,errors}/, apps/api/src/identity/principal.helper.ts, packages/modules/identity-tenant-billing/src/domain/permission-evaluator.ts, packages/platform/src/application/unit-of-work/
confidence: verified

### Login (OIDC + PKCE)
trigger: user clicks login
steps:
1. POST /v1/auth/login mints state/nonce/code_verifier, sets short-lived cookies, returns authorizeUrl with S256 challenge = BASE64URL(SHA256(verifier)).
2. Auth0 redirects GET /v1/auth/callback; state/nonce/verifier validated (CSRF/replay guard).
3. exchangeCode → validateIdToken (issuer/audience/nonce) → upsert app_user → createAtLogin records ip/user-agent, rotates session.
4. Session cookie set; ephemeral cookies cleared.
files: apps/api/src/identity/auth.controller.ts, packages/modules/identity-tenant-billing/src/infrastructure/auth0/live-identity-provider.ts, src/application/session-service.ts
confidence: verified

### Tenant Creation & Trial Start
trigger: authenticated user creates workspace
steps: one transaction writes tenant + Owner membership + role evidence + TRIALING subscription (14 days, provider NULL, zero PayPal contact) + entitlement projection + audit + outbox(tenant.created).
files: packages/modules/identity-tenant-billing/src/application/tenant-service.ts, docs/project/FLOWS/IDENTITY_BILLING.md
confidence: verified

### Subscription Verification (PayPal)
trigger: subscriber completes PayPal approval; frontend posts subscription id
steps:
1. Backend retrieves subscription from PayPal adapter (browser claim insufficient).
2. Six rules: plan id matches expected plan code → plan.product matches expected product → currency USD → amount equals configured minor units → provider status acceptable → custom_id binds calling tenant.
3. State change routed through canTransitionSubscription (illegal/regressive transitions rejected); entitlement projected only from ACTIVE-derived states; immutable billing_event recorded; audit/outbox emitted.
files: packages/modules/identity-tenant-billing/src/application/paypal-verification-service.ts, src/application/billing-webhook-service.ts, src/domain/subscription-state.ts, apps/api/src/identity/billing.controller.ts
confidence: verified

### PayPal Webhook Intake
trigger: PayPal POSTs /v1/billing/paypal/webhook
steps: raw-body Fastify plugin (scoped parser) → signature+webhook-id verification (production rejects ALL webhooks when PAYPAL_WEBHOOK_ID unset) → dedupe on provider_event_id → persist outcome immutably → legal transition only → projection + audit/outbox; duplicates re-return original outcome without overwriting; out-of-order cannot regress state.
files: apps/api/src/main.ts (route registration), billing-webhook-service.ts
confidence: verified

### Outbox Delivery
trigger: committed transaction wrote outbox_event
steps: worker polls (250ms) → claims batch FOR UPDATE SKIP LOCKED as mushagil_relay → publishes to BullMQ queue → worker handler consults processed_event ledger (logical exactly-once) → consumer effect (e.g. probe_projection row) → ack; failures retry exponentially then DLQ (metric exposed).
files: apps/worker/src/outbox-worker.ts, packages/platform/src/infrastructure/outbox/outbox-relay.ts, src/infrastructure/queue/processed-event-guard.ts, docs/project/FLOWS/OUTBOX_DELIVERY.md
confidence: verified

### Draft→Publish Business Truth (M03)
trigger: owner finishes editing business profile/services/hours and calls publish
steps:
1. Draft edits land in draft tables with optimistic versions (If-Match).
2. ReadinessService evaluates blockers (BLOCKING severity refuses publish).
3. PublicationService loads entire draft truth, resolves hours/policy/knowledge/service pricing into a self-contained JSONB document, hashes canonically, inserts append-only business.business_publication row — all in one tx with audit+outbox.
4. All downstream reads (offering resolution, future public booking/AI) go through PublishedTruthService reading ONLY publications; old publications remain byte-identical.
files: packages/modules/business-capacity/src/application/{publication-service,published-truth-service,readiness-service}.ts, docs/adr/0004-published-business-truth-snapshots.md, apps/api/src/business/business-profile.controller.ts (POST /publish)
confidence: verified

### Weekly Hours Authoring
trigger: operator sets split/overnight opening hours or staff schedule
steps: authored rule rows (day_of_week ISO, start_minute, duration_minutes) + derived week-minute segments written in one tx; domain rejects overlaps first (precise message naming conflicting interval); DB GiST exclusion constraint backstops including week-wrap (rule past Sunday becomes segments [start,10080)+[0,overflow)); wall-clock→UTC conversion at read time in location IANA zone.
files: packages/modules/business-capacity/src/domain/{opening-hours,week-time}.ts, migration 0004 (location_hours_segment etc.), docs/adr/0005-weekly-time-rules-and-derived-segments.md
confidence: verified

### Trial Expiry Sweep
trigger: BullMQ repeatable job hourly
steps: TrialExpiryService.sweepDueTrials scans TRIALING subscriptions past 14 days → transitions TRIALING→EXPIRED (legal transition) → emits billing.trial_expired evidence; skip-to-next scheduling means outage causes at most one delayed run.
files: apps/worker/src/trial-expiry-worker.ts, src/application/trial-expiry-service.ts
confidence: verified

## APIS

Conventions: all routes prefixed `/v1`; success envelope `{data, meta:{correlationId, freshnessAt}}`; errors `{error:{code,message,correlationId,retryable,fields,details}}`; cursor pagination default 25/max 100; mutating updates require If-Match version (422 when absent, 409 VERSION_CONFLICT when stale); 404 (not 403) for other-tenant resources. Representative significant routes:

| method | route | handler file:symbol | auth | notes |
|---|---|---|---|---|
| POST | /v1/auth/login | apps/api/src/identity/auth.controller.ts:login | none | sets PKCE/state/nonce cookies, returns authorizeUrl |
| GET | /v1/auth/callback | auth.controller.ts:callback | none | validates state/nonce, exchanges code, creates session |
| POST | /v1/auth/dev/fake-login | auth.controller.ts | none | fake IdP only; refused in production mode |
| POST | /v1/auth/logout | auth.controller.ts | session | |
| POST | /v1/tenants | tenants.controller.ts:create | anyAuthenticated | atomic tenant+Owner+trial tx |
| GET | /v1/tenants | tenants.controller.ts:list | anyAuthenticated | own memberships only |
| POST | /v1/tenants/:id/switch | tenants.controller.ts:switch | member | changes active workspace |
| GET | /v1/tenants/:tenantId/members | members.controller.ts:list | role-gated | |
| POST | /v1/tenants/:tenantId/invitations | members.controller.ts:invite | invite perm | hashed single-use invitation |
| POST | /v1/tenants/:tenantId/members/:id/role | members.controller.ts:changeRole | grant ceiling | Admin cannot create Owner |
| POST | /v1/tenants/:tenantId/members/:id/status | members.controller.ts:setStatus | suspend/remove | last-owner protected (DB trigger) |
| POST | /v1/invitations/accept | members.controller.ts:accept | none (capability) | hashed token, single-use |
| GET/POST | /v1/sessions, /v1/sessions/:id/revoke | sessions.controller.ts | session/self | immediate effect via principal re-read |
| GET | /v1/billing/plans | billing.controller.ts | session | public-read plan table |
| GET | /v1/billing/subscription | billing.controller.ts | tenant member | |
| POST | /v1/billing/subscriptions/verify | billing.controller.ts | tenant member | six-rule PayPal verification; state machine |
| POST | /v1/billing/paypal/webhook | apps/api/src/main.ts (raw Fastify route) | signature+PAYPAL_WEBHOOK_ID | raw-body parser scoped to route; dedupe; fail-closed |
| CRUD | /v1/platform/probes | platform-probes.controller.ts | tenant | M01 proof domain |
| GET | /internal/v1/ping | internal/internal.controller.ts | InternalGuard (API key) | proves internal workload surface auth |
| GET/PUT | /v1/business/profile | business-profile.controller.ts | resource.action manifest | If-Match versioned |
| GET | /v1/business/readiness | business-profile.controller.ts | | blocker list |
| POST | /v1/business/publish | business-profile.controller.ts | publish perm | refuses on BLOCKING readiness |
| GET | /v1/business/publications(/:id), /published | business-profile.controller.ts | | immutable snapshots |
| CRUD | /v1/business/knowledge(+conflicts) | knowledge.controller.ts | | entryKey draft/publish/archive |
| CRUD | /v1/business/locations(+hours,+closures) | locations.controller.ts | | hours rules→segments; closures tstzrange |
| * | /v1/business/onboarding(advance,complete) | onboarding.controller.ts | | resumable step machine |
| * | /v1/business/packs(install,migrate,rollback…) | packs.controller.ts | | hash-pinned pack lifecycle |
| GET/PUT | /v1/business/policies(draft,publish,published) | policies.controller.ts | | booking policy versioning |
| POST | /v1/catalog/offerings/resolve | offerings.controller.ts | | deterministic resolver against published truth |
| CRUD | /v1/catalog/services(+draft,publish,archive-impact) | services.controller.ts | | service/version/variant |
| CRUD | /v1/catalog/skills | skills.controller.ts | | |
| * | /v1/catalog/staff(+skills,eligibility,schedule,time-off,archive-impact) | staff.controller.ts | | weekly schedule + time off w/ exclusion constraints |
| * | /v1/catalog/resources(types,+capacity,+blocks,archive) | resources.controller.ts | | capacity N; blocks tstzrange |

## DATABASE

Engine: PostgreSQL 18. Two app schemas.

**platform** (delivery spine + identity):
- `audit_event` — append-oriented actor-attributed audit written in the same tx as mutations.
- `outbox_event` — transactional events awaiting relay (claimed SKIP LOCKED).
- `processed_event` — consumer dedupe ledger (logical exactly-once).
- `idempotency_key` — request/result idempotency (canonical request hash; same key+different payload ⇒ IDEMPOTENCY_CONFLICT).
- `platform_probe` / `probe_projection` — M01 end-to-end proof pair (API row → worker projection).
- `schema_migration` — migration bookkeeping (global RLS exemption #1).
- `tenant`, `membership` (role/status), `invitation` (hashed single-use expiring), `role_grant` (append-only evidence), `security_event`, `auth_session` (rotatable/revocable), `app_user` (Auth0-linked global shadow — global RLS exemption #2), `plan` (public-read via USING(true) policy — avoided a third exemption), `subscription` (TRIALING→ACTIVE→PAST_DUE→GRACE→SUSPENDED→CANCELED/EXPIRED state machine), `billing_event` (immutable core + provider_event_id dedupe), `entitlement` (feature/limit projection).

**business** (29 tables, migration 0004): business_profile; business_publication (whole-truth JSONB + canonical hash + readiness eval, append-only); location + location_hours (authored rules) + location_hours_segment (derived int4range[0,10080) w/ GiST exclusion) + location_closure (tstzrange exclusion); booking_policy (versioned); knowledge_entry (versioned, conflict detection); onboarding_state; industry_pack_definition + pack_installation + pack_custom_field (retained read-only when referenced) + pack_migration; service + service_version (immutable published versions) + service_variant + service_skill_requirement + service_resource_requirement; skill; resource_type + resource + resource_block (tstzrange); staff + staff_schedule + staff_schedule_segment (GiST) + staff_break + staff_time_off (tstzrange exclusion partial on status='APPROVED').

Mechanics: UUIDv7 ids; timestamptz UTC + IANA tz columns; integer-minor-unit money; composite `(parent_id, tenant_id)` FKs against parent `unique(id, tenant_id)`; forced RLS everywhere except the two reviewed exemptions; last-owner DB trigger; migration runner enforces checksums + advisory locks; `mushagil_relay` has zero grants in `business` (ADR 0003). No vector store, no separate cache layer beyond Redis/BullMQ. Event catalog: docs/project/DATA_EVENTS.md lists 11 internal event types (probe.*, tenant.created, membership.*, invitation.*, billing.*).

## TESTS

Frameworks: Vitest 4.1.11 everywhere (single root vitest.config.ts), Playwright chromium for e2e. ~122 test files. Commands are stable root scripts routed by quality/suite-registry.json globs with module-status gating: a suite whose owning module isn't DONE prints SUITE_NOT_YET_REQUIRED; a DONE module whose suite matches zero files fails SUITE_EMPTY (anti-cheat, tamper-tested, M01 evidence). Script-runner suites: openapi drift, architecture (depcruise), secrets, sbom, permissions.

Layout: `<pkg>/tests/{unit,integration,contracts,component,e2e,a11y,rtl,security,migrations,permissions,concurrency}/...`. Unit tests have no DB/network; integration uses real ephemeral PostgreSQL + Redis with real migrations (packages/database/tests/support/ephemeral-db.ts); e2e runs real web+api+worker with zero route interception (browser creates probe in ar+en, polls real probe_projection row).

Coverage mapping highlights:
- database: rls-invariant (all app schemas), rls-tenant-isolation, rls-missing-tenant, unit-of-work-atomicity (forced audit failure rolls back), outbox-relay (3 concurrent relays), processed-event-dedupe, queue-dlq-retry, queue-prefix-isolation, version-conflict, business-schema-invariants, prior-to-head (previous release → head), least-privilege role tests.
- identity-tenant-billing: permission-manifest + business-catalog-manifest (verify:permissions), last-owner race (real concurrent Promise.allSettled), PKCE binding (tamper-verified: reintroducing raw-verifier fails exactly 175/176), LiveIdentityProvider direct test, webhook forged/duplicate/out-of-order/wrong-product cases incl. named refusal of legacy plan P-83S97234B32877119NKFP42Y.
- business-capacity: 13 unit suites (pricing/duration/intake/capacity/eligibility/opening-hours/state-machines/readiness/…) + integration (publication-lifecycle, concurrency, impossible-config-and-impact, tenant-isolation-and-entitlements, audit-and-outbox).
- api: http-harness round trips (identity, billing verify, business flow, catalog concurrency, staff).
- web: component/a11y/rtl/e2e incl. business-setup-journey and business-permission-denied e2e.
Latest full green counts (M02 evidence, orchestrator-run): unit 176, integration 60, migrations 13, security 22, permissions 9, component 47, rtl 29, a11y 13, e2e 3; concurrency/performance/ai-evals/restore report SUITE_NOT_YET_REQUIRED (owners M05/M09/M07/M09).

## GIT LESSONS

Only 8 commits; work lands as large module commits followed by sha-recording doc commits (be19e93 m01a, 4595034 m01b, 45d77b7 m01c, 8b1389a m02, 638838a docs). No reverted commits exist; "reverted approaches" appear as review findings fixed before landing:

- 8b1389a/M02 evidence — **PKCE bug**: authorize declared S256 but sent the raw verifier as challenge; would have failed 100% of real logins; fake IdP didn't verify the binding so no test caught it. Lesson: fakes must enforce the same cryptographic bindings as live providers; a direct LiveIdentityProvider test was added after a second pass found the regression guard only covered the fake. Structural gap pattern: "the test layer that mirrors where the bug lived was missing".
- 8b1389a/M02 evidence — **state-machine bypass**: subscribe-verify endpoint collapsed APPROVAL_PENDING/APPROVED to PAST_DUE (illegal from TRIALING) and could overwrite terminal states; zero non-mocked coverage. Lesson: every write path must funnel through the same canTransition function as the primary path.
- M02 advisory fixes — duplicate webhook overwrote original billing_event.outcome; ENTITLEMENT_LIMIT_REACHED corrected 403→409 (capacity bucket per contract §7).
- 45d77b7/M01 evidence — **UI hang on fetch rejection**: genuine network failure left probes screen and dialogs permanently hung; added retryable NETWORK_UNAVAILABLE code, finally-reset submit state, offline detection on mount.
- Dangerous areas flagged by design: anything touching RLS exemptions (exactly two, invariant-tested), mushagil_relay grants, the raw-body Fastify plugin scoping in apps/api/src/main.ts (registering the content-type parser at root would silently flip every JSON route to raw strings), and the week-minute segment derivation.
- apps/worker/src/outbox-worker.ts:14–20 — a comment previously blamed the queue name for a consumer hang; actual cause was Queue and Worker sharing one Redis connection (fixed via duplicate()). Lesson: verify blame empirically before writing it down.
- Migration discipline lesson (0003 in M02): close deferred FK debt with NOT VALID + VALIDATE forward migrations; never rewrite already-shipped migrations.
- Doc-drift hazard in progress right now: staged deletion of ARCHITECTURE.md/CLAUDE.md/QUALITY.md while source comments still cite them (grep "ARCHITECTURE" in packages/modules/identity-tenant-billing/src).

## DECISIONS

- Modular monolith, 3 processes, no microservices/K8s/Tailwind/GraphQL/second DB — startup simplicity with strict boundaries — MODULES.md engineering contract §1 + .dependency-cruiser.cjs.
- PostgreSQL as sole truth; Redis only transport; commitment exists only post-commit — MODULES.md §4, DATA_EVENTS.md.
- Forced RLS + composite tenant FKs + server-derived tenant authority (never body/query/header/model output) — MODULES.md §2, ADR 0003, common/tenant/*.
- Central PermissionEvaluator with manifest rows; deny-by-default; nobody grants above own rank; 404-not-403 non-enumeration — permission-evaluator.ts:1–19, roles.ts.
- One transaction = mutation + audit + outbox; provider calls banned inside tx via AsyncLocalStorage guard — transaction-guard/guard.ts, DATA_EVENTS.md.
- Per-module DB schema (`business`) instead of piling tables into `platform`; RLS invariant generalized over APP_SCHEMAS list — ADR 0003.
- Immutable whole-business JSONB publication snapshots as the only published truth (vs filtering drafts on status) — ADR 0004, publication-service.ts.
- Weekly hours authored as rules + derived week-minute segments with GiST exclusion (overnight = two segments) instead of circular-range arithmetic — ADR 0005.
- M03 ships without remote import despite conditional contract; SSRF surface deliberately nonexistent — ADR 0006.
- Provider modes {live,sandbox,fake} with production fail-closed refusal — provider-mode.ts, M01 acceptance.
- Domain subscription states decoupled from PayPal enums; APPROVAL_PENDING/APPROVED ⇒ no local transition — subscription-state.ts.
- Suite registry gated by MODULES.md status so commands never silently match zero tests — scripts/run-suite.mjs, quality/suite-registry.json.
- Raw Fastify encapsulated plugin for the PayPal webhook only (scoped content-type parser) — apps/api/src/main.ts:100–140.

## RISKS & TECH DEBT

- **~136 dirty files / M03 uncommitted**: the entire business-capacity + packs implementation, migration 0004, and ~60 new test files exist only in the working tree; loss risk plus documentation contradiction (docs/project/CURRENT_STATE.md still says "M03 NOT_STARTED, next eligible"). Evidence: git status.
- **Doc drift**: ARCHITECTURE.md/CLAUDE.md/QUALITY.md deleted in working tree but cited throughout code comments ("ARCHITECTURE decision #6/#11", "§9") — future agents following those pointers will dead-end.
- **Lost-response robustness gap**: retry after genuinely lost response on tenant-create / invitation-accept errors instead of returning the original result (documented known limitation, M02 evidence).
- **Trial tier ambiguity**: trial previews GROWTH entitlement; product contract doesn't fix a trial tier (config-driven).
- **Publication document growth**: single denormalized JSONB row per publication; acknowledged scaling ceiling in ADR 0004 (chunk/compress when it matters).
- **Permissive rate limit placeholder**: @fastify/rate-limit max=100000/min effectively disabled (apps/api/src/main.ts:142) — fine pre-launch, must be revisited before exposure.
- **Scratch files at root**: check-redis.mjs (hardcoded socket path debug script, untracked).
- **Single-consumer outbox**: most emitted events (tenant.created, membership.*, invitation.*) have no consumer yet — relying on outbox rows without projections is fine now but silent until modules land.
- **Raw SQL breadth in business-capacity**: publication/offering services hand-roll large parameterized queries; correct but heavy maintenance surface, and cross-schema joins are not DB-forbidden (ADR 0003 consequences).
- **Live-provider activation debt**: Auth0 tenant, PAYPAL_WEBHOOK_ID registration (needs public HTTPS endpoint), PayPal browser SDK checkout (manual stand-in labelled in SubscribeDialog) — all fail closed but block real users.
- **No staging/production infra reality**: infra/environments contain only READMEs; CI is the only execution environment beyond local.

## UNCERTAIN

- Whether the working-tree M03 work passes its full gate suite (MODULES.md M03 Evidence block is "_Not yet completed_"); I did not run the test suites (read-only analysis).
- Exact final route count/shape of /v1/business/** and /v1/catalog/** may shift before the module lands (uncommitted).
- Who/what the orchestrator is operationally (AI implementer sessions implied by MODULES.md evidence wording and deleted CLAUDE.md; humans in the loop unclear).
- Target hosting/cloud choice for staging/production (no IaC beyond compose; infra README contents suggest intent only).
- Whether docs/adr/0001–0002 exist elsewhere (only 0003–0006 + README present in docs/adr; numbering implies earlier ADRs were consolidated or lost in the doc reorg).
- Performance characteristics of publication building on large businesses (single-tx full-document rebuild) — unmeasured.
- The `.env` / `.env.local` files exist locally but were intentionally not read (secret hygiene); only .env.example variable names are reported.
