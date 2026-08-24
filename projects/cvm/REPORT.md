# CORTEX REPORT — CVM

## META
project_id: cvm
root: /home/aboud/Dev/CVM
kind: pnpm-workspace monorepo; modular monolith (Fastify API + pg-boss worker + singleton scheduler) + Next.js operator console + offline Python ML; branch `redesign/cvm-console` with ~53 dirty files (mid visual-redesign)
languages: TypeScript (Node >=22, ESM), Python 3.12+ (`ml/`), SQL (23 raw up/down migration pairs), k6 JS load scripts
frameworks: Fastify 5 + Zod v4 (+ fastify-type-provider-zod; OpenAPI 3.1 generated from Zod), Next.js ^16.3 App Router / React ^19.2 (100% server-rendered, zero client JS by design), Tailwind CSS v4, pg-boss ^12 (jobs), node-postgres `pg` + drizzle-orm helpers re-exported via `@cvm/platform/db`, OpenTelemetry + pino, Argon2id, openid-client (SSO/SCIM); ML: numpy/pandas/scikit-learn via uv
package_managers: pnpm@9.15.4 (workspace: apps/* packages/*), uv for `ml/`
test_frameworks: vitest 4 (projects `unit` = `*.unit.test.ts`, `integration` = `*.int.test.ts` against real Postgres via Testcontainers/compose), Playwright (e2e/golden-path.spec.ts, 24 tests), pytest (`pnpm ml:test` → `cd ml && uv run pytest -q`), k6 + tsx harnesses (tools/loadtest)
deployment: docker-compose (dev: postgres 18-alpine, minio, otel-collector, prometheus, tempo, loki, grafana), root Dockerfile (multi-stage), reference compose deploy/compose.ref.yml, deploy/helm (K8s, commit 746d389), GitHub Actions (.github/workflows/ci.yml: static job → integration job with Postgres service; migrations up/down/up, RLS drift, tests, e2e, image scan)

## OVERVIEW

CVM Intelligence Platform is an enterprise multi-tenant Customer Value Management platform for telecom operators: ingest raw event feeds under data contracts, resolve them into canonical customers, decide what to offer each person through a governed decision engine, run campaigns that deliver the offers across channels, and prove afterwards what happened and why. The product's self-declared core claim is **traceability** (PRD §39): any delivered message is one screen away from the decision, candidates, denials, model scores, delivery receipts and conversions behind it (`/trace/{deliveryId}`, e2e golden path v8). Target: "first sellable enterprise release" 30 Sep 2026; a v1.0 release record exists (docs/releases/v1.0.md) with every gate measured and its gaps stated honestly.

Architecture in one line: four processes over one Postgres. `apps/api` (Fastify, routes only), `apps/worker` (pg-boss consumers only), `apps/scheduler` (self-electing singleton that registers recurring jobs via advisory lock), `apps/web` (Next.js RSC console that proxies to the API server-side; browser never calls the API directly). All domain logic lives in 21 modules under `packages/modules/*`, each behind a facade `index.ts`; shared infrastructure lives in `packages/platform/*` which may not import any domain module (ADR-001, enforced by dependency-cruiser in CI). Postgres is the only datastore (ADR-004): RLS-isolated tables, monthly-partitioned append-only event log, pg-boss queues in schema `pgboss`, outbox relay, idempotency keys, materialised Customer 360 projection. MinIO/S3 holds batch file bytes only, behind `ObjectStorePort`. `ml/` is deliberately offline-only Python (no DB connection, serves no request).

The repo is unusually documentation-dense and honesty-obsessed: PRODUCT.md/DESIGN.md written *from* the built product, ADR index tracking post-implementation status with amendments as separate files, phase completion docs, runbooks, a security self-review that names "the reviewer wrote the code" as its own unmet requirement, and hard UI rules ("no mock screens", synthetic data always labelled, unmeasurable KPIs render as absent-not-zero). The current branch carries an in-flight console redesign (~53 modified web pages, fonts deleted, docs/design/REDESIGN_BRIEF.md added) [uncertain how it relates to HEAD's "Treg" design language vs STATUS.md's ALLOCATION system].

Known honest gaps at v1.0 (docs/releases/v1.0.md): §36 item 8 FAILS (no message ever sent through a real ESP/SMS provider — sandbox-proven only); churn-model metrics degenerate on synthetic data; no soak test; alert metrics exist but are not routed to a receiver; security review and runbook execution lack independent witnesses; five sign-off roles unsigned.

## ARCHITECTURE

**Processes** (all share one Postgres):
- `apps/api/src/main.ts` → `app.ts` `buildApp()`: composition root. Registers helmet/CORS/cookie, custom JSON parser (empty body = `{}`), swagger (OpenAPI 3.1 from Zod), `registerPipeline()` (platform/http/plugin.ts), health routes, then one prefixed plugin block `/api/v1` registering 22 route plugins from all domain modules (apps/api/src/app.ts:244-270). SCIM mounts at root `/scim/v2` per RFC 7644 (app.ts:280). Injects ports at composition root: `setAuthenticator(IamAuthenticator)`, `setEntitlementChecker` (commercial packaging gate), `setSecurityAuditSink` (denials audited), `setScoreProvider(onlineScoreProvider(batchScoreProvider))`.
- `apps/worker/src/main.ts`: imports every job-defining module (side-effect registration), subscribes `identity.changed` outbox events → reprojects both customers' profiles, starts `startJobs({work:true})`, starts low-latency trigger realtime dispatch (failure non-fatal — batch jobs still dispatch), graceful shutdown lets in-flight handlers finish to avoid double-sends.
- `apps/scheduler/src/main.ts`: acquires Postgres advisory lock (`AdvisoryLock(LOCK_KEYS.scheduler)`), exits cleanly if another instance holds it; concatenates each module's `_SCHEDULE` export and registers cron entries via `startJobs({work:false,schedule:true})`.
- `apps/web`: Next.js App Router; `src/proxy.ts` forwards pathname via header so nav/band theming resolves server-side; static CSP in next.config.ts deliberately blocks Next's client bootstrap so plain-form POST/303 works without hydration; i18n en/ar with key = English source string, locale cookie, RTL via CSS logical properties (apps/web/src/lib/i18n.ts).

**Request pipeline** (packages/platform/src/http/plugin.ts, ~330 lines, ADR-003): correlation → log → rate-limit pass 1 (IP, pre-auth) → authn → tenant resolution/binding (x-tenant-id header must match membership; cross-tenant attempt returns identical 403 and is security-audited) → rate-limit pass 2 (api-key/tenant-quota aware) → authorization (permission + fail-closed tenant-match check + entitlement gate) → idempotency claim/replay/store → handler → metrics/access-log → error mapper (RFC 9457 problem+json; DB-down→503+Retry-After; unexpected unique violation→409; bare ZodError→400). Boot-time onRoute guard: every route MUST declare access rule, and every mutating route MUST declare `audited` or `auditExempt` or the process refuses to start.

**Jobs/events**: pg-boss in same Postgres; enqueue transactional with the causing write (ADR-006); module-defined jobs via `defineJob` listed in per-module `_JOBS` arrays; recurring crons in `_SCHEDULE`; maintenance module relays `outbox_message` rows (e.g. `identity.changed`) to subscribers. Composition-root wiring of routes/jobs/schedules is mechanically verified by `tools/wiring/check.ts` (see GIT LESSONS).

**External integrations**: delivery channel adapters email/SMS/signed webhook (HTTP-native, no vendor SDKs; per-credential circuit breaker; kill switch), provider receipt webhook `POST /api/v1/webhooks/delivery`, source connectors with SSRF guard refusing link-local/loopback at DNS resolution (commit 3438097), OIDC SSO + SCIM 2.0 provisioning, OTLP → collector → Tempo/Loki/Prometheus/Grafana, MinIO object store.

**Observability**: one correlation id flows HTTP→logs→traces→jobs→audit→decision→delivery→conversion (PRD §39); pino logs with proven PII redaction (packages/platform/__tests__/redaction.unit.test.ts); telemetry started via `--import` bootstrap.mjs because ESM hoisting silently attaches instrumentation to nothing (worker/scheduler main.ts header comment, fix 8fe2f61).

## MODULES

### apps-api — Fastify HTTP API
purpose: serve the versioned REST contract; composition root wiring platform ports to module implementations.
path_prefixes: apps/api/
key_files: apps/api/src/app.ts, src/main.ts, src/health.ts (liveness vs readiness), src/openapi-dump.ts, src/jobs.ts
entrypoints: `pnpm dev:api`; buildApp() exported for integration tests
responsibilities: register pipeline + 22 module route plugins under /api/v1; SCIM at root; publish openapi.json publicly; empty-body-tolerant JSON parser; bodyLimit 5MB rejects oversized ingestion at edge.
invariants: this is the ONLY place knowing both platform and modules (ADR-001); every route declares permission/public/authenticated at boot; trustProxy on; requestIdHeader x-correlation-id.
pitfalls: Fastify default parser rejects empty JSON bodies (custom parser added after activation routes 400'd); logger:false avoids duplicate context-free log lines.
confidence: verified

### apps-worker — pg-boss job consumer
purpose: execute all background work; never serves requests.
path_prefixes: apps/worker/
key_files: apps/worker/src/main.ts
entrypoints: `pnpm dev:worker`
responsibilities: import side-effect-registers every module's jobs; subscribeToOutbox('identity.changed') reprojects merge/unmerge parties; startRealtimeDispatch for triggers (optional, degrades to batch); graceful SIGTERM within 30s so non-idempotent sends don't double.
invariants: job handlers finish before exit (retry-after-kill would mean doing work twice, P6 = sending twice).
pitfalls: a dev worker left running during `pnpm test` steals batch leases and makes tests no-op (release record known-limitation 14).
confidence: verified

### apps-scheduler — recurring-job registrar (singleton)
purpose: evaluate pg-boss cron and enqueue recurring jobs; enqueues, never executes.
path_prefixes: apps/scheduler/
key_files: apps/scheduler/src/main.ts
entrypoints: `pnpm dev:scheduler`
responsibilities: tryAcquire advisory lock; loser exits cleanly; registers MAINTENANCE/INGESTION/.../EXPERIMENT_SCHEDULE entries.
invariants: singleton enforced by session-scoped Postgres lock, not replica count — rolling updates otherwise run nightly retention N times; lock auto-releases on crash.
pitfalls: missing scheduler looks like a product bug — outbox.relay never fires, merge-reprojection waits 90s (playwright.config.ts comment; CI fixed in ef6ca9a).
confidence: verified

### apps-web — Next.js operator console
purpose: bilingual (en/ar RTL) permission-gated console; 100% RSC, zero client interface JS.
path_prefixes: apps/web/src/
key_files: src/proxy.ts, src/app/layout.tsx, src/app/(app)/layout.tsx, src/components/ui.tsx, src/components/band-rail.tsx, src/components/rule-builder.tsx, src/lib/api.ts (apiOrEmpty/mutate helpers), src/lib/api-types.ts (generated), src/lib/i18n.ts, src/lib/dictionaries/ar.ts, next.config.ts (static CSP)
entrypoints: `pnpm dev:web` (:3100); login page standalone.
responsibilities: 41 pages across 22 sections ((app)/customers|identity|audiences|offers|decisions|campaigns|deliveries|journeys|triggers|loyalty|games|models|analytics|data-quality|integrations|privacy|audit|administration|trace…); forms POST server actions answered 303 with ?error/?notice params; rule-builder round-trips AST as URL JSON; disclosure via `<details>`; no modals.
invariants: permissions gate navigation (absent, not disabled) while server re-checks; CSP `script-src 'self'` without unsafe-inline is LOAD-BEARING (keeps client router dead so native form posts carry Set-Cookie); apiOrEmpty distinguishes 403 from honest-empty; Arabic uses Latin digits (ar-u-nu-latn); dir set once on html; logical properties everywhere.
pitfalls: enabling per-request nonce broke sign-in + seven golden-path tests, reverted twice independently (0283a39, STATUS.md); renaming page headings broke 11 heading-based tests (reverted); `--text-muted`/`--border-strong` contrast failures found by redesign audit; Tailwind v4 needs `[var(--token)]` not v3 `[--token]` shorthand.
confidence: verified

### platform — @cvm/platform infrastructure kernel
purpose: config/context/contracts/crypto/db/events/http/jobs/storage/telemetry; imported by everyone, imports NO domain module.
path_prefixes: packages/platform/src/
key_files: db/pool.ts, db/migrate.ts, db/check-rls.ts (6-assertion drift guard), db/schema/index.ts (TENANT_SCOPED_TABLES/PARTITIONED_TABLES/SYSTEM_TABLES registry), http/plugin.ts, http/idempotency.ts, http/ratelimit.ts, http/quota.ts, jobs/index.ts (defineJob/startJobs), jobs/install.ts, storage (ObjectStorePort → S3/MinIO), telemetry/bootstrap.mjs, context/index.ts (ambient request context)
entrypoints: subpath exports package.json#exports (./db, ./http, …)
responsibilities: pool ownership (only platform/db touches pools — dependency-cruiser rule), migrations runner with owner/runtime role split, RLS drift guard, pg-boss lifecycle + install into `pgboss` schema, HTTP pipeline (above), Argon2id crypto, OTel bootstrap.
invariants: runtime DB role has no BYPASSRLS and no DDL; partitions created via SECURITY DEFINER functions; statement timeout configurable.
pitfalls: ESM hoisting defeats startTelemetry() in-process (bootstrap via --import); caught unique violations abort Postgres txns (25P02) — use ON CONFLICT clauses.
confidence: verified

### modules-iam — Identity & Access Management
purpose: users, roles/personas, permissions (30 domain perms, 10 persona roles), sessions (opaque, server-side), Argon2id auth, MFA (TOTP+recovery), API keys (embed tenant — ADR-016), service accounts, SSO (OIDC), SCIM 2.0 at /scim/v2, org units, session policy, IP allow-listing.
path_prefixes: packages/modules/src/iam/
key_files: iam/index.ts (exports IamAuthenticator consumed via platform port — ADR-014), application/, http/routes.ts
entrypoints: authRoutes, iamAdminRoutes, scimRoutes, ssoRoutes registered in app.ts
responsibilities: authenticate() port impl; permissionsFor(tenantId) — permission sets are tenant-paired; login failure/permission-denial audited via sink.
invariants: separation of duties — admin@example.com deliberately cannot read customers/campaigns/analytics.
pitfalls: SSO/SCIM wiring exposed three bugs on landing (d81b9a5); SCIM must live outside /api/v1 or Okta-style base URLs break.
confidence: strongly_inferred

### modules-ingestion — ingestion, contracts, quarantine, quality
purpose: data sources/contracts, batch file ingest, eight §7.3 quality detections, quarantine with reasons + replay, event-type/schema registry, retention.
path_prefixes: packages/modules/src/ingestion/
key_files: application/, infrastructure/, http/routes.ts, jobs.ts
entrypoints: ingestionRoutes (/v1/ingest/*, /v1/data-contracts*, /v1/data-quality*)
responsibilities: validate against contracts before accept; duplicates counted not accepted (re-ingest → 0 accepted/25 duplicates); late events land in correct monthly partition with late_count.
invariants: batch counters exactly-once under concurrent runners (fixed a7907e9); ingestion key cannot rewrite its validating contract (e2e negative test).
pitfalls: stale-source metric didn't exist until game-day scenario 1 demanded it.
confidence: verified

### modules-identity — identity resolution & merge
purpose: deterministic cross-source resolution into canonical customers; ambiguous cases raise identity_conflict (never auto-merge); reversible merge/unmerge; probabilistic review queue (P10); rules configuration.
path_prefixes: packages/modules/src/identity/
key_files: application/resolve.ts, merge.ts, conflicts.ts, rules.ts, probabilistic-review.ts; jobs.ts
entrypoints: identityRoutes (/v1/identity/*)
responsibilities: publish `identity.changed` outbox events in the same txn as change (ADR-006) naming surviving/merged/restored customer ids.
invariants: merge→unmerge restores profile/timeline/features exactly (golden-path v3 assertion).
pitfalls: reading only one payload key left the other party describing "a person who no longer exists in that shape" (worker main.ts comment).
confidence: verified

### modules-profile — Customer 360 projection
purpose: materialised per-customer profile (not a view), timeline, PII masking, gated+audited export.
path_prefixes: packages/modules/src/profile/
key_files: application/project.ts (idempotent projector writing nothing when unchanged), read.ts, masking.ts, export.ts; jobs.ts
entrypoints: profileRoutes (/v1/customers/{id} cluster, 13 operations incl. export)
responsibilities: rebuild from identity graph on identity.changed; projection state tracked in profile_projection_state.
invariants: projector idempotent; export audited; masked fields by permission.
pitfalls: category-filter 500-then-nothing bug (55d8c35); "a file load about somebody is not that person doing something" timeline semantics fix (802f6c5).
confidence: verified

### modules-features — feature platform
purpose: declarative feature definitions compiled to SQL (definitions ARE data — ADR-017), versioned; freshness, lineage; read model customer_feature_current split from record feature_value.
path_prefixes: packages/modules/src/features/
key_files: application/, infrastructure/ (compiler), http/routes.ts, jobs.ts
entrypoints: featureRoutes (/v1/feature-definitions*)
responsibilities: every value records definition version + computed-at; never-computed reads as absent, never 0; changing computation creates new version.
invariants: same compiler used by training extraction and serving (kills train/serve skew at source).
pitfalls: highest-scoring customer labelled `low` bucket bug (594c702).
confidence: strongly_inferred

### modules-segments — audiences & rule language
purpose: one versioned JSON rule AST (ADR-012) validated against closed per-tenant field catalogue, compiled to parameterised SQL; preview estimate, materialisation, schedules, explain-one-customer walking same AST, exclusions.
path_prefixes: packages/modules/src/segments/
key_files: application/catalogue.ts, segments.ts, preview.ts, materialize.ts, explain.ts, exclusions.ts; domain/; infrastructure/
entrypoints: segmentRoutes (/v1/segments*, /v1/segment-fields)
responsibilities: prefer feature read-model over event scan when compiling; reproducible re-materialisation writes nothing.
invariants: nothing user-written becomes SQL string — keys/values bound as parameters; rule naming `city; drop table customer--` refused at catalogue (security review).
pitfalls: recursive AST needed named schemas in OpenAPI (jsonSchemaTransformObject) or generated types failed.
confidence: verified

### modules-catalog — offer catalog
purpose: offers with sixteen §11 fields, immutable versions, separation-of-duties approval, transactional capacity (offer_inventory CHECK constraint prevents oversell).
path_prefixes: packages/modules/src/catalog/
key_files: application/ (incl. offerabilityProblems consumed by gate), http/routes.ts
entrypoints: catalogRoutes (/v1/offers*)
responsibilities: expose offerability checks to PolicyGate; inventory reservation via conditional UPDATE WHERE (no SELECT FOR UPDATE serialisation).
invariants: unapproved offer never returned by a decision (gate 1 evidence).
confidence: strongly_inferred

### modules-consent — consent & contact policy
purpose: append-only consent records, suppression entries, do-not-contact, quiet hours in customer timezone, frequency caps, contact policies per channel, policy packs.
path_prefixes: packages/modules/src/consent/
key_files: application/ (checkFrequency, checkQuietHours, checkSuppression, currentConsent, policyFor), http/routes.ts
entrypoints: consentRoutes
responsibilities: supply the ordered check functions the single PolicyGate runs; consent.* became evaluable AST fields in P5 exactly as ADR-012 promised.
invariants: consent withdrawal between approval and send suppresses the send (release-blocking test).
confidence: strongly_inferred

### modules-decision — decision engine (gate + ranker)
purpose: PRD §21 eleven-step NBA: candidates from catalog → eligibility/policy BEFORE ranking → pure ranker over survivors with no catalog access (type-signature-enforced, ADR-008 ScoreProvider port) → selection or first-class NO_ACTION with denial codes; full candidate trace.
path_prefixes: packages/modules/src/decision/
key_files: application/gate.ts (PolicyGate evaluate(), CHECK_ORDER 1..7: consent, suppression, quietHours, frequency, eligibility, inventory, campaignConflict; denials accumulate, unevaluable check fails closed immediately), application/decide.ts, rank.ts, weights.ts, trace.ts, scores.ts; domain/codes.ts (POLICY_VERSION, DenialCode); http/routes.ts
entrypoints: decisionRoutes (/v1/decisions, /batch ≤500, /{id}, /summary, /policy/evaluate simulator, /decision-codes, /decision-weights)
responsibilities: gate split customer-half (once/decision) + offer-half (once/candidate) — evaluation strategy, same functions; deterministic given inputs+policy version.
invariants: ranker cannot reach catalog; SCORE_UNAVAILABLE declared rather than substituting zero; trace stores whole candidate set (reproducibility unit = the trace).
pitfalls: normalised margin is the one set-relative term; capacity reservation must be conditional UPDATE not lock.
confidence: verified

### modules-campaigns — campaign orchestration
purpose: campaigns with fourteen §12 fields, immutable versions, ten pre-launch checks, separation-of-duties approval (409 on launch without; self-approval refused), frozen audience snapshots, targets, runs, funnel snapshots, kill switch with documented halt bound, attribution windows/method-on-every-number.
path_prefixes: packages/modules/src/campaigns/
key_files: application/, domain/, http/routes.ts, jobs.ts
entrypoints: campaignRoutes (/v1/campaigns*, /v1/runs/{id}, /v1/campaign-states)
responsibilities: create→validate→approve→execute loop; typed confirmation for accidental-launch scenario; funnel reconciles against raw tables via callable endpoint.
invariants: delivery state machine belongs to `delivery` NOT here (putting it here created an import cycle — the layering was pointing at the truth).
confidence: verified

### modules-delivery — execution engine & channels
purpose: effectively-once send execution (ADR-010): claim row in delivery_attempt unique (tenant_id, dedupe_key) BEFORE provider call; four adapters (email/SMS/webhook + sandbox fixture); receipts parsing idempotent; retry classification; per-credential circuit breaker (NOT per provider — two tenants sharing a provider have different reputations); provider credentials encrypted.
path_prefixes: packages/modules/src/delivery/
key_files: application/send.ts, credentials.ts, receipts.ts, trace.ts; infrastructure/adapters.ts; domain/state.ts, adapter.ts
entrypoints: deliveryRoutes (/v1/deliveries/{id}, /v1/provider-credentials*, /v1/webhooks/delivery, /v1/templates*, /v1/channels, /v1/t/{token} tracker)
responsibilities: queued→submitted→delivered/failed/expired state machine; timeout classified `unknown` (retried EXACTLY once, cap is a constant); adapters speak raw HTTP not vendor SDKs so retries stay visible above the claim.
invariants: never-twice-by-us (a timeout leaves visible queued row); known-failed send may be RE-claimed under same row — without this the claim defeated retry and messages silently never sent (game day worst defect); ON CONFLICT DO NOTHING RETURNING not caught violation (25P02 aborts tx — bit twice).
confidence: verified

### modules-experiments — A/B experiments & outcomes
purpose: deterministic sticky bucketing, control declared first, held-out customers still measured; variants, assignments, sequential stopping, bandit reallocation; conversion attribution inside declared window with method named on every number; uplift NULL without holdout.
path_prefixes: packages/modules/src/experiments/
key_files: application/, http/routes.ts, jobs.ts
entrypoints: experimentRoutes (/v1/experiments*, /reallocate)
confidence: strongly_inferred

### modules-analytics — analytics & KPIs
purpose: executive KPIs computed at read time; cohorts, behaviour funnels, trends, affinity, segment overlap, attribution comparison; panel naming what is deliberately NOT reported; unmeasurable renders as reason-not-zero.
path_prefixes: packages/modules/src/analytics/
key_files: application/, http/routes.ts
entrypoints: analyticsRoutes (/v1/analytics/executive|cohorts|behaviour-funnel|trend|affinity|segment-overlap|attribution-comparison)
confidence: strongly_inferred

### modules-ml — model registry & scoring (platform side of Track B)
purpose: governed model objects (ADR-009): model/version/deployment/metric/drift_check/challenger/shadow_score/retrain_policy — six-ish tenant-scoped RLS tables audited like offers; deployment requires second-person approval; undeployed version cannot write scores the decision path reads; online inference provider wrapping batch floor; dataset snapshots; customer_score carries model_version_id.
path_prefixes: packages/modules/src/ml/
key_files: ml/index.ts (mlRoutes, onlineScoreProvider, batchScoreProvider), application/, jobs.ts (nightly batch scoring)
entrypoints: mlRoutes (/v1/models*, /v1/models/{code} 13 ops incl /operations, /v1/datasets/{id})
responsibilities: scorer refuses artifact formats it cannot evaluate (sets artifact_uri for tree models instead of guessing); extraction runs platform feature compiler with occurred_at < as_of point-in-time bound.
invariants: train/serve skew checked by test replaying trainer predictions to 1e-9 (packages/modules/__tests__/ml-skew.unit.test.ts).
confidence: verified

### modules-privacy — erasure & governance
purpose: right-to-erasure requests (approval-gated, irreversible): personal data removed, audit trail intact, aggregates unmoved — payload KEY REMOVAL only through the one narrow append-only breach path; processing register; jurisdiction consent packs; hashed compliance exports.
path_prefixes: packages/modules/src/privacy/
key_files: privacy/application/, http/routes.ts
entrypoints: privacyRoutes (/v1/erasure-requests*, /erasure-scope, /governance/*)
invariants: erasure cannot rewrite WHAT happened, only WHO it was about (ADR README Phase 7).
pitfalls: quarantined-row erasure is substring-matched — malformed identifier text evades it (known limitation 10).
confidence: strongly_inferred

### modules-audit — append-only audit trail
purpose: audit_event append-only at DB level; searchable; correlation-joined; /audit/correlation/{id} shows everything in one action.
path_prefixes: packages/modules/src/audit/
key_files: audit/index.ts (recordAudit), http/routes.ts
entrypoints: auditRoutes
invariants: mutating routes must declare audited/auditExempt at boot (pipeline guard); security denials recorded in ACTOR'S tenant.
confidence: verified

### modules-maintenance — outbox relay & housekeeping
purpose: outbox_message relay to subscribers (outbox.relay cron), retention enforcement, partition creation via SECURITY DEFINER, dashboard metrics.
path_prefixes: packages/modules/src/maintenance/
key_files: maintenance/index.ts, MAINTENANCE_SCHEDULE
confidence: strongly_inferred

### modules-triggers + modules-journeys + modules-loyalty — P8/P9 surface
purpose: trigger_rule evaluation (realtime dispatch listener in worker + batch fallback), journey builder/versions/instances/node-state, loyalty programs/tiers/ledger/redemptions/promotions, games/gamification participation. Present, wired, and screens shipped (commits 1a4baeb, 47ea930) though README lists journeys/loyalty as roadmap-absent-from-nav pre-P8 [uncertain which statement reflects current nav].
path_prefixes: packages/modules/src/triggers|journeys|loyalty/
entrypoints: triggerRoutes, journeyRoutes, loyaltyRoutes; TRIGGER/JOURNEY schedules registered; worker imports all three.
confidence: inferred

### tools/ + ml/ — fixtures, ops drills, offline ML
purpose: datagen (deliberately dirty synthetic telco dataset — 53k customers/3.38M events fixture), seed (dev tenant+admins), provision (end-to-end tenant provisioning), gameday (12 failure scenarios) + restore drill, loadtest (ingest ack, c360 read, segment materialise, decision latency, ui worst-screen, k6 js), i18n check/sweep, db/init-roles, wiring/check.ts, ml tools extract→train→register + fixture loader; ml/ Python package cvm_ml (train, evaluate, dataset, card) offline-only.
path_prefixes: tools/, ml/
key_files: tools/wiring/check.ts, tools/datagen/generate.ts, tools/loadtest/ui-apis.ts, ml/src/cvm_ml/train.py
confidence: verified

## FLOWS

### Ingestion → quarantine → replay
trigger: POST /v1/ingest/{source_code} batch upload or scheduled connector pull
steps: 1. contract validation per data_contract 2. accepted rows → partitioned customer_event append-only log; bad rows → ingestion_error/quarantine with reasons 3. quality detections update data_quality_metric 4. duplicates counted on batch (0 accepted/25 dup) 5. replay from quarantine screen
files: packages/modules/src/ingestion/**, migrations 0005/0006/0007, e2e/golden-path.spec.ts:361,531
confidence: verified

### Identity resolve → merge/unmerge → C360 reprojection
trigger: ingestion of identifiers; manual conflict resolution; POST /v1/identity/merge|unmerge
steps: 1. deterministic resolution; ambiguity raises identity_conflict (queue) 2. merge writes identity_merge + link events and publishes identity.changed OUTBOX ROW IN SAME TXN 3. maintenance outbox.relay delivers to worker 4. worker maps ALL THREE payload ids → enqueueProfileProjection 5. idempotent projector rebuilds both profiles from restored graph
files: apps/worker/src/main.ts:51-71, packages/modules/src/identity/application/merge.ts, packages/modules/src/profile/application/project.ts, e2e golden-path "merge reprojects both customers"
confidence: verified

### Audience build → materialise → explain
trigger: UI rule builder (AST in URL) → POST /v1/segments; schedule
steps: 1. validate AST vs closed field catalogue 2. preview count estimate 3. compile preferring feature read-model, parameterised SQL 4. exclusions subtract provably 5. segment_run materialises membership 6. explain walks same AST for one customer
files: packages/modules/src/segments/application/*.ts, docs/rule-ast.md, e2e:1094,1348
confidence: verified

### Offer approve → decision (gate+rank) → NO_ACTION possible
trigger: POST /v1/decisions (or /batch ≤500)
steps: 1. candidates from catalog 2. customer-half gate checks 1-4 once 3. per-offer checks 5-7 (eligibility/inventory/campaign conflict) 4. ranker = pure fn over survivors, score via ScoreProvider (online fresh else batch floor) 5. select top or NO_ACTION with denial codes 6. reserve capacity conditionally 7. persist decision + EVERY candidate with denial code + policy version
files: packages/modules/src/decision/application/gate.ts, decide.ts, rank.ts, http/routes.ts:127, e2e:1453,1748
confidence: verified

### Campaign approve → run → deliver (effectively-once) → receipts → funnel
trigger: campaign launch (requires approval + typed confirm)
steps: 1. freeze audience snapshot into campaign_target 2. run creates delivery jobs 3. CLAIM delivery_attempt row ON CONFLICT DO NOTHING RETURNING unique (tenant_id,dedupe_key) BEFORE provider call 4. PolicyGate RE-EVALUATED per send (consent withdrawn post-approval ⇒ suppressed) 5. adapter raw-HTTP send w/ dedupe key as idempotency key 6. receipt webhook updates state machine idempotently 7. kill switch cancels remaining targets 8. funnel snapshot reconciles vs raw
files: packages/modules/src/delivery/application/send.ts, infrastructure/adapters.ts, packages/modules/src/campaigns/**, apps/api/__tests__/delivery-idempotency.int.test.ts, e2e:1867,2264
confidence: verified

### §39 end-to-end trace
trigger: GET /v1/trace/{deliveryId}; console /trace/[id]
steps: joins campaign_run → profile → feature values (with def versions) → decision + all candidates/denials → model registry → delivery_attempt → receipts → engagement/conversions; each link states present-or-why-absent; correlation id joins audit
files: packages/modules/src/delivery/application/trace.ts, apps/web/src/app/(app)/trace/[id]/page.tsx, e2e:2708
confidence: verified

### Governed ML lifecycle (Track B)
trigger: pnpm ml:load-fixture → refresh-features → train; then API approve/deploy
steps: 1. TS extractor pulls point-in-time features (occurred_at < as_of) via platform compiler 2. Python trains/evaluates offline, label = tenant-configured churn definition on dataset_snapshot 3. register model_version 4. SECOND PERSON approves (self refused) 5. deploy makes version live 6. nightly batch scoring writes customer_score w/ model_version_id; online provider computes fresh when deployed+features present 7. skew test replays trainer predictions to 1e-9 8. rollback operation audited
files: ml/src/cvm_ml/train.py, tools/ml/train.ts, packages/modules/src/ml/**, e2e:2371,2650
confidence: verified

### Right to erasure
trigger: POST /v1/erasure-requests → approval
steps: 1. scope query (/erasure-scope) 2. remove personal payload KEYS ONLY through narrow append-only path 3. profile reprojected 4. audit_event intact 5. aggregates unmoved 6. quarantined rows substring-matched [limitation]
files: packages/modules/src/privacy/**, migration 0013_erasure, e2e:2786,2919
confidence: strongly_inferred

## APIS

Conventions: all under `/api/v1` except SCIM (`/scim/v2/Users` RFC 7644), `/health`, `/ready`, public `/api/v1/openapi.json`. Auth: session cookie (`cvm_session`) OR `Authorization: Bearer <api-key>`; every route declares `permission` (30 domain perms) / `authenticated` / `public` — undeclared refuses boot; mutating routes declare `audited|auditExempt`; optional `Idempotency-Key` (same key+different body ⇒ 409; replay header `idempotency-replayed`); errors RFC 9457 problem+json with stable type URI + correlation_id; RateLimit-* headers (per-replica caveat documented); tenant via x-tenant-id header validated against membership. Contract committed at docs/api/openapi.json (218 paths) with `pnpm openapi:check` drift gate; frontend types generated (apps/web/src/lib/api-types.ts). Full surface too large for a table — representatives below.

| method | route | handler file:symbol | auth | notes |
|---|---|---|---|---|
| POST | /api/v1/auth/login | packages/modules/src/iam (authRoutes) | public | Argon2id; constant-fail wrong creds |
| GET | /health, /ready | apps/api/src/health.ts:registerHealthRoutes | public | liveness ≠ readiness; /ready names DB; DB-down ⇒ 503+Retry-After |
| POST | /api/v1/decisions | packages/modules/src/decision/http/routes.ts:127 (decisionRoutes) | decision.request, audited | §21 NBA; dry_run flag; NO_ACTION outcome |
| POST | /api/v1/decisions/batch | decision/http/routes.ts:159 | decision.request | ≤500; same engine per customer |
| POST | /api/v1/policy/evaluate | decision module (simulator) | decision.read? | exposes gate halves; accumulates denials |
| GET | /api/v1/trace/{deliveryId} | packages/modules/src/delivery/application/trace.ts | gated | §39 eight answers one screen |
| POST | /api/v1/ingest/{source_code} | packages/modules/src/ingestion | api-key typical | batch; quarantine reasons |
| GET/POST | /api/v1/segments, /{key} (11 ops) | packages/modules/src/segments | segment.read/manage | preview/materialise/explain/version |
| POST | /api/v1/identity/merge, /unmerge | identity/application/merge.ts | identity.manage | reversible; emits identity.changed |
| GET | /api/v1/customers/{id} (13 ops cluster) | packages/modules/src/profile | customers.read | C360 blocks; masked; /export audited+gated |
| POST | /api/v1/campaigns/{code}/launch etc (7 ops) | packages/modules/src/campaigns | campaign.manage | 409 without approval; kill endpoint |
| GET | /api/v1/models/{code} (13 ops) | packages/modules/src/ml | models.* | approve/deploy/score/rollback/challenger |
| POST | /api/v1/webhooks/delivery | delivery (receipts.ts) | signed webhook | provider receipt contract docs/delivery-webhooks.md |
| GET/POST | /api/v1/erasure-requests | packages/modules/src/privacy | privacy.* | approval-gated irreversible |
| GET | /api/v1/audit/correlation/{correlationId} | packages/modules/src/audit | audit.read | everything in one action |
| CRUD | /scim/v2/Users | packages/modules/src/iam scimRoutes | SCIM token | mounted at ROOT, not /api/v1 |

## DATABASE

Engine: PostgreSQL only (ADR-004). Dev compose postgres:18-alpine; release record reference says Postgres 16 local [discrepancy noted]. Roles: `cvm_owner` (DDL/migrations) vs `cvm_app` runtime (no BYPASSRLS, no DDL). Migrations: 23 numbered pairs `*.up.sql/*.down.sql` (0001_platform … 0023_sso_lookup_policies), ~6,156 up-lines, runner packages/platform/src/db/migrate.ts with status/rollback; all rolled back-to-zero-and-rebuilt against populated DB as DoD proof. Jobs schema `pgboss` installed separately (jobs:install). Drizzle ORM present for typing/helpers; migrations are raw SQL.

Tenant isolation (ADR-005 + amendments 005-A1 nullsafe policies, 005-A2 self-membership): RLS ENABLE + FORCE on tenant-scoped tables; `tenant_isolation` policy keyed on current_setting; unbound query returns ZERO rows (missing-data symptom, never leak); leading-column tenant_id indexes required; runtime-created partitions carry OWN policies; SECURITY DEFINER functions own DDL. Guard: db/check-rls.ts asserts classification/tenant_id/RLS/FORCE/index/isolation-suite-membership/partition-policy — 74 tables protected at v1.0; restore drill counted 95 tables + 16 partitions.

Notable entities WITH MEANING: `tenant`,`tenant_entitlement`(packaging gate),`tenant_quota`; IAM `app_user`,`session`(opaque server-side),`api_key`(tenant embedded ADR-016),`service_account`,`scim_token`,`role`,`role_permission`,`organization_unit`; `audit_event`(append-only, correlation-joined); data backbone `data_source`,`data_contract`,`event_type_definition`,`customer_event`(monthly PARTITIONED append-only log, THE record — dedupe key includes partition key per ADR-007-A1),`ingestion_batch`,`ingestion_error`(quarantine),`retention_policy`; identity `customer`,`customer_identifier`,`identity_link_event`,`identity_merge`,`identity_conflict`; C360 `customer_profile`(MATERIALISED projection not view),`customer_attribute`,`contact_log`; features `feature_definition`(compiled SQL, versioned),`feature_value`(lineage: def version+computed_at),`customer_feature_current`(read model); `dataset_snapshot`(churn label = tenant config),`customer_score`(carries model_version_id); audiences `segment`,`segment_version`,`segment_membership`,`segment_run`,`segment_schedule`,`exclusion_list(+_member)`; offers `offer`,`offer_version`(immutable),`offer_inventory`(CHECK prevents oversell); consent `consent_record`(append-only),`contact_policy`,`suppression_entry`,`consent_policy_pack`; decisions `decision`,`decision_candidate`(EVERY candidate + denial code),`decision_weight_config`; campaigns `campaign(+_version,_target,_run,_funnel_snapshot)`; delivery `delivery_attempt`(unique (tenant_id,dedupe_key) claim-before-send),`delivery_receipt`,`provider_credential`,`message_template`,`engagement_event`,`conversion`; experiments `experiment(+_variant,_assignment)`; models `model`,`model_version`,`model_deployment`,`model_metric`,`model_drift_check`,`model_challenger`,`model_shadow_score`,`model_monitor_sample`,`model_retrain_policy`; governance `erasure_request`,`processing_record`,`compliance_export`; loyalty `loyalty_program/_tier/_membership/_ledger/_reward/_redemption/_earn_rule/_promotion`; journeys `journey(+_version)`,`journey_instance`,`journey_node_state`; gamification `game`,`game_participation`,`game_progress_event`; infra `outbox_message`,`idempotency_key`,`schema_migration`.

No vector store, no Redis/Kafka/ClickHouse anywhere. Cache = materialised tables + customer_feature_current. Object storage (MinIO/S3) only for batch FILE bytes behind ObjectStorePort.

## TESTS

Frameworks: vitest 4 two projects (vitest.config.ts): `unit` (*.unit.test.ts, node env) and `integration` (*.int.test.ts, REAL Postgres via Testcontainers/compose — "a mocked database cannot prove RLS isolation", ADR-005 note; fileParallelism:false, 120s timeouts). Playwright: e2e/golden-path.spec.ts, 24 tests, workers=1 fullyParallel:false (sequential — parallel would interleave audit rows), runs from EMPTY database, requires api+worker+scheduler already running (Playwright starts only web). pytest for ml/ (12 tests). Load: k6 + tsx harnesses (tools/loadtest) gating ingest-ack p95<200ms, c360 p95<300ms, decision p95<500ms, UI worst-screen <500ms, segmentation SLA. Gameday: 12 failure scenarios (tools/gameday).

Layout/coverage mapping: packages/modules/__tests__ (25 files: resolution, decision, campaigns, features, segments, journeys, loyalty, bandit, inference, mfa, model-ops, triggers, ml-skew ← Python/TS parity 1e-9, connectors…), packages/platform/__tests__ (tenant-isolation.int ← every RLS table; transactional-jobs.int ← ADR-006; redaction.unit ← PII logs; object-store.int; telemetry.int), apps/api/__tests__ (13 int: api, decisioning, profile, ml, identity, campaigns, segments, ingestion, scim, delivery-idempotency, erasure, rate-limiting, cross-tenant-permissions, role-catalogue), apps/web/__tests__/i18n.unit.test.ts, ml/tests/test_train.py.

Counts at v1.0 (docs/releases/v1.0.md Gate 4): 912 vitest + 24 e2e + 12 python; 160-test tenant isolation suite; 0 boundary violations across 302 modules.

Commands: `pnpm test|test:unit|test:integration|e2e|verify` (verify = lint+typecheck+typecheck:web+boundaries+wiring:check+i18n:check+test), `pnpm db:check-rls`, `pnpm openapi:check`, `pnpm boundaries`, `pnpm ml:test`, `pnpm gameday|gameday:restore`, loadtest:* suite. CI (.github/workflows/ci.yml): red pipeline blocks merge, no override; static job (<1min) then integration job with postgres service running migrations up/down/up, RLS drift, integration, e2e, image scan. Known trap: dev worker must be stopped during `pnpm test` (lease stealing makes tests no-op).

## GIT LESSONS

Durable lessons with shas (short shas, branch redesign/cvm-console):

- **"Verified but never wired" — the wiring gate (a1e2e0f, tools/wiring/check.ts docstring).** Phase 10 shipped eight capabilities (online inference, probabilistic identity, three score families, attribution comparison, source connectors, SSO, SCIM) built, tested, documented, each with passing unit tests AND facade exports — and NO caller, so screens showed empty tables forever with the suite green. Lesson: a unit test proves a function WORKS, nothing proved it RUNS; composition roots need mechanical checks. Design choices worth copying: check `register(name)` not the import line (an imported-but-unregistered plugin passes every diff-based grep); scope it small — the earlier 178-finding exhaustive sweep produced a check nobody reads; deliberate dormancy goes in docs/dormant-exports.txt WITH A REASON.
- **CSP is load-bearing, reverted twice (48cfc42 broke every form; 0283a39 revert "it was load-bearing, and e2e caught it"; STATUS.md command-palette nonce attempt broke 7 golden-path tests again).** The static policy blocking Next's inline bootstrap keeps the client router dead so native form POST→303 carries Set-Cookie. Enabling per-request nonce silently kills sign-in. Lesson: a "security header" can be the mechanism keeping an architecture alive; e2e is what catches architecture-level regressions unit suites cannot see.
- **ESM import hoisting silently disables instrumentation (8fe2f61 "telemetry produced zero spans under ESM").** startTelemetry() inside the entrypoint runs after patched modules loaded. Fix: --import bootstrap.mjs. Now documented atop worker/scheduler mains.
- **The scheduler nobody starts (ef6ca9a fixed CI; playwright.config.ts + STATUS.md warn).** Only the scheduler evaluates pg-boss cron; without it outbox.relay never fires and merge-reprojection hangs 90s — absence looks exactly like a product bug. Lesson: singleton background processes need explicit presence in dev docs and CI.
- **Caught unique violations poison Postgres transactions (df4137c, Phase 6 section of docs/adr/README.md).** 25P02 aborts subsequent statements; bit twice (delivery claim + conversion attribution). Fix: `ON CONFLICT DO NOTHING RETURNING` which never raises.
- **Two correct pieces composed into silent data loss — game-day worst defect (docs/releases/v1.0.md Gate 2).** Retryable 5xx left target unprocessed "for next pass"; next pass saw ADR-010 claim taken and skipped forever; run reported completed. Fixes: known-failed claims may be RE-taken under the same row; claim predicate and shouldRetry share ONE predicate (off-by-one left attempts stuck `queued`). Lesson: idempotency claims and retry logic must be designed together or each defeats the other.
- **Concurrency doubles counters (a7907e9 "two runners on one ingestion batch double its counters").** Batch-level idempotency needed explicit concurrency tests.
- **Dependency failure is 503+Retry-After, never 500 (game-day scenario 6; plugin.ts:549-561).** 500 means "our bug" — LB keeps instance, clients don't retry, engineers hunt ghosts. Same reasoning mapped unexpected unique violations to 409 with a human sentence.
- **Migration hygiene: expand/contract enforced; 0004 violation recorded not hidden (6c4a029 → PHASE-01-COMPLETION.md).** N-1 image ran against current schema as acceptance (scenario 10).
- **Web Docker image had NEVER built until 0012387** — image builds belong in CI early.
- **Reverted redesign sweeps documented so they stay dead (b4fbbc2 → docs/design/STATUS.md).** Numbering conditionally-rendered regions produces meaningless gaps; renaming headings to job-descriptions broke 11 getByRole-heading tests — tests identify pages by heading, so that's a product decision not a refactor. Also font self-hosting forced by next/font/google pinning a stale CDN URL that 404'd clean builds (48cfc42, DESIGN.md).
- **Small honesty bugs the redesign surfaced:** "Models (0)" shown while eight existed (bd920f1); highest-scoring customer labelled `low` (594c702); timeline filter 500→empty (55d8c35). Lesson: derived labels/counters need their own tests.
- **Dangerous areas:** consent/policy ordering (fail-closed semantics), delivery claim↔retry interplay, scheduler singleton, partition RLS at runtime, tenant binding in pipeline hook 4, .env pointing DATABASE_URL at 5432 while the project DB lives on 5433 (STATUS.md "would save the next person an hour").

## DECISIONS

- Modular monolith with enforced boundaries — monorepo risk of module spaghetti — dependency-cruiser 10 rules in CI (`pnpm boundaries`): facade-only imports, platform never imports domains, domain/ excludes frameworks, only platform/db owns pools; loosening requires ADR amendment — README.md layout note, docs/adr/README.md ADR-001 row.
- TypeScript platform + Python strictly offline ML — avoid dual-language serving path — extraction and scoring stayed in TS so models train on the SAME feature compiler the serving path reads; seam guarded by prediction-replay test to 1e-9; tree formats refused via artifact_uri — docs/adr/README.md "Track B", packages/modules/__tests__/ml-skew.unit.test.ts.
- Fastify + Zod as single source of truth — schema drift between validation/docs/types — validator+serializer compilers, OpenAPI 3.1 emitted, committed contract with CI drift gate feeding generated frontend types — apps/api/src/app.ts:97-201, package.json openapi:check.
- Postgres is the only datastore — operational simplicity, transactional guarantees — even queues (pg-boss), outbox, idempotency, projections live in PG; object storage only for opaque bytes — ADR-004 + amendments.
- Tenant isolation triple-layered — cross-tenant leak is existential for enterprise — FORCEd RLS + restricted runtime role + CI suite attacking every tenant-scoped table; unbound query returns zero rows — ADR-005/-A1/-A2, db/check-rls.ts, packages/platform/__tests__/tenant-isolation.int.test.ts.
- Transactional job enqueue — lost-work windows between write and job — pg-boss row commits atomically with domain row — ADR-006, transactional-jobs.int.test.ts.
- One PolicyGate, fail-closed, re-checked at send time — consent withdrawn after audience build is THE compliance failure — seven ordered checks, denials accumulate for diagnosability, unevaluable check denies immediately; signature forces delivery to consume it — packages/modules/src/decision/application/gate.ts:21-41, README.md.
- Rule AST is data, never SQL — injection + explainability + reuse across segments/eligibility/exclusions — closed field catalogue, parameterised compilation, explainer walks the same AST — ADR-012, docs/rule-ast.md.
- Effectively-once delivery via DB uniqueness — provider duplicates are the classic CVM wound — claim-before-send on unique (tenant_id,dedupe_key), dedupe key passed to provider as ITS idempotency key; honestly named never-twice-by-us, not exactly-once — ADR-010, delivery-idempotency.int.test.ts.
- No client JavaScript in the console — density, RTL correctness, accessibility, CSP-friendly — RSC + server actions + URL state; proxy.ts pathname header; controls styled as elements — PRODUCT.md constraints, apps/web/src/proxy.ts, DESIGN.md.
- Honesty conditions as release gates — credibility of an operator tool — no mock screens, synthetic labelled everywhere, unmeasurable ≠ zero, failing item reported as FAIL — PRODUCT.md, docs/releases/v1.0.md.
- Feature definitions are data compiled to SQL; read/record split — lineage questions ("what did this number mean at decision time") must stay answerable — versioned definitions, values carry def version+time — ADR-017.
- API keys embed their tenant (new from implementation) — auth-time tenant scoping without lookup round-trip — docs/adr/016-api-key-tenant-embedding.md.

## RISKS & TECH DEBT

- §36 item 8 permanently open until a real ESP/SMS account exists; adapters sandbox-proven only (docs/releases/v1.0.md Gate 1).
- Churn-model metrics degenerate (ROC-AUC 1.0 on 91.8%-positive label) — pipeline real, model placeholder; synthetic flatters everything (risk T3).
- No ≥2h soak test; alert RULES not wired to a receiver; security review self-authored; runbooks never executed by a second person; §39 demo unwitnessed; five sign-offs unsigned (same document).
- ENCRYPTION_KEY rotation manual (no automated re-encryption); encryption at rest delegated to deployment and off here.
- Quarantined-row erasure substring-matched — malformed identifier text evades erasure (known limitation 10).
- Golden path consumes ~55 of 60/min login budget — cannot run twice in a minute (limitation 13).
- Rate limits enforced per replica — N replicas multiply ceiling (documented in OpenAPI description).
- .env DATABASE_URL port mismatch (5432 vs actual 5433 container) traps setup (STATUS.md).
- Redesign WIP: ~53 dirty files, old fonts deleted (amiri/fraunces/martian woff2 gone from working tree) while DESIGN.md still documents Readex Pro/Martian Mono; HEAD ("Treg OpenRouter system", 2d7ffce/0dbc4bc) vs STATUS.md ALLOCATION vs new REDESIGN_BRIEF.md — three design narratives coexist; docs/design/STATUS.md gates list may be stale.
- ~110 tables still lack magnitude-column alignment (Data Quality is the pattern; header-only alignment worse than none — STATUS.md).
- Stages 05–15 information-architecture restructuring unfinished; pages carry new tokens but old layouts.
- Command palette blocked pending backend work (session cookie must survive client router) — documented as decide-not-guess.
- Journeys/loyalty/gamification completeness ambiguous: README says "absent from UI, not stubbed" while modules/screens/APIs/jobs exist (commits 1a4baeb, 47ea930; worker imports them) [needs reconciliation].
- Throughput figures are single-machine floors; no scale claim beyond 53k customers (PRD §29 posture).

## UNCERTAIN

- Exact relationship/state of the three design narratives in the working tree (HEAD Treg commits vs ALLOCATION DESIGN.md vs dirty 53-file diff adding REDESIGN_BRIEF.md and deleting fonts) — did not run the app or inspect every diff hunk.
- drizzle-orm's precise role (dependency + imported operators like `and/eq/sql` via @cvm/platform/db) — whether any query building is drizzle-based vs raw SQL strings was not exhaustively traced.
- Whether docs/dormant-exports.txt currently exists/populated (read returned empty at analysis time) — wiring allowlist contents unverified.
- Helm chart depth in deploy/helm (existence verified via ls + commit 746d389; not audited).
- Postgres version discrepancy: release record says "Postgres 16 local", compose pins 18-alpine — which is authoritative for the reference deployment is unresolved.
- Current test counts vs v1.0's 912/24/12 (post-Phase-10 additions not re-counted; file counts here: 21 unit + 11 int under packages/, 13 int under apps/api, plus web/tools stragglers).
- ml/pyproject pins numpy/pandas/scikit-learn but per-package internals (train.py algorithm details, card.py content) were not read.
- Whether `t/{token}` click tracker and `/v1/contact_log` write path cover all four advertised channel adapters equally (adapters.ts not fully read).
- games/gamification module placement (screens exist at apps/web (app)/games; assumed part of loyalty/adjacent modules — not traced to a dedicated packages/modules/src directory).
