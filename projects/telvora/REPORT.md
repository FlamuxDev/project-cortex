# CORTEX REPORT — Telvora

## META
project_id: telvora
root: /home/aboud/Dev/Telvora
kind: pnpm monorepo; multi-tenant telecom CVM (Customer Value Management) SaaS platform — Go modular monolith + Python ML sidecar + Next.js console/public site
languages: Go 1.26 (services/core-api), TypeScript 6.0.3 (web/e2e/packages), Python 3.14 (services/ml), SQL (73 files: 36 migration pairs + db/init role script)
frameworks: Go stdlib net/http (no web framework), pgx/v5 + golang-migrate (only runtime deps in go.mod); Next.js 16.3.1 / React 19.2.8 / Tailwind CSS 4; FastAPI + psycopg + scikit-learn/LightGBM-class ML stack (services/ml); AWS CDK (infra/cdk); Playwright; k6
package_managers: pnpm 9.15.4 (workspace root package.json, pnpm-workspace.yaml), go modules, pip venv (Makefile bootstrap)
test_frameworks: go test (149 *_test.go incl. live-Postgres RLS isolation suites), pytest (services/ml/tests), Playwright e2e (38 spec files, chromium-en + chromium-ar projects), k6 load suites (load/)
deployment: dev = docker-compose (postgres:18 + valkey:8); prod = AWS via two CDK stacks (TelvoraFoundation ECR, TelvoraPlatform: ECS Fargate multi-AZ, RDS PostgreSQL 18, EFS, HTTPS ALB) deployed by GitHub Actions OIDC on v* tags with a `migrate bootstrap-up` Fargate barrier (docs/adr/0006, .github/workflows/deploy.yml)
git_state: branch master, 59 commits, working tree DIRTY (~237 files: 212 modified, 25 untracked). Analyzed as-is. Untracked = post-RC hardening wave (ADR-0006, infra/cdk/lib+scripts, deploy.yml, packages/contracts OpenAPI, migrations 0035/0036, migrate bootstrap.go, internal/db/url.go, model monitoring compat, ml tests) + one stray PNG named `--full-page` at repo root.

## OVERVIEW

Telvora is a complete, release-candidate multi-tenant Customer Value Management platform for telecom operators, built by an agent-driven protocol (AGENT_BUILD_PROTOCOL.md) through 42 sequential phases B00–B41, each with a verification exit gate (commit series `43e75c1`…`cdc2036`). It ingests telecom source data (CRM/billing/usage/CDR/recharge/care/network/consent/catalog), maps it to a canonical tenant-scoped model, resolves identities into golden records, computes features, and drives governed growth loops: segments → offers → consent-checked, approval-gated campaigns/journeys → A/B experiments with incremental attribution — plus a deterministic real-time next-best-action decision API and a governed LLM layer that can draft/explain but never act unapproved (RELEASE_NOTES.md).

Architecture is deliberately a **modular monolith** (ADR-0001): one Go binary (`services/core-api`) holding ~30 domain packages behind explicit store/handler seams, with only the ML service split out for runtime reasons, and background workers as goroutines inside the same process tree (ingestion dispatcher, journeys scheduler, model-monitoring sweeper, retention purger — cmd/server/main.go:247-261). Multi-tenancy is pooled Postgres with mandatory FORCE Row-Level Security keyed off a per-transaction `app.tenant_id` GUC set server-side only (ADR-0002, internal/db/context.go). Cloud-shaped infra (S3/SQS/Kinesis) is represented locally by honest Postgres/filesystem adapters behind narrow interfaces so the swap is additive (ADR-0004).

The frontend (`apps/web`) is a Next.js App Router application split into `(marketing)` public bilingual EN/AR site, `(auth)` screens, and `(protected)` console (~74 routes inventoried in docs/UX_REDESIGN_AUDIT.md), talking to core-api over REST via typed lib clients (src/lib/*.ts). Shared UI primitives/tokens/i18n live in workspace packages. A post-B41 "product redesign" pass (context.md, commits `cfae43f`…`209528e`) restructured IA and landing/auth pages.

Current dirty state is the **post-RC hardening wave** (described in RELEASE_NOTES.md header): committed API contracts (packages/contracts/openapi), production AWS IaC + deploy pipeline, partition-RLS hardening migration 0035, bounded large-population model monitoring 0036, and the self-service signup feature already committed earlier (`cfae43f`). The tree should be treated as RC + uncommitted hardening; nothing here is mid-refactor garbage except the stray `--full-page` PNG [verified: PNG magic bytes].

## ARCHITECTURE

- **core-api** (Go, `services/core-api`): single HTTP process, entrypoint `cmd/server/main.go` wiring ~201 routes onto stdlib `http.ServeMux` with method patterns, wrapped in `httputil.CorrelationMiddleware`. Two pgx pools: app pool (`DATABASE_URL`, restricted role `telvora_app`) and worker pool (`WORKER_DATABASE_URL`, restricted role `telvora_worker` with exactly one cross-tenant RLS policy on queue_message — main.go:66-73, db/init/01-app-role.sql).
- **In-process workers** (same binary, goroutines, main.go:247-261): ingestion queue dispatcher (2s tick), journey wait/resume scheduler (2s), model drift/performance monitor (5min, calls ml service), retention purge worker (1h).
- **ml** (Python FastAPI, `services/ml/app/main.py`): pure compute sidecar — `/train`, `/score`, `/healthz`. Its ONE caller is Go `internal/models.MLClient`; it never writes registry rows itself (module docstring, main.py:1-21). Connects to the same Postgres under the same RLS GUC discipline (app/db.py docstring).
- **web** (Next.js, `apps/web`): route groups `(marketing)/(auth)/(protected)` under `[locale]`; locale redirect middleware `src/proxy.ts`; server-side session guard `src/lib/guard.ts` ("hidden navigation is not authorization"); one thin API client per backend domain in `src/lib/*.ts`.
- **Shared contracts**: `packages/contracts` generates `coreApiOperations` list + OpenAPI JSONs from main.go (scripts/generate-core-openapi.mjs header comment) — CI-checkable drift detection [inferred from "Generated … do not edit" + openapi/ dir].
- **Queues/streams**: Postgres-backed `queue_message` (SQS shape: visibility timeout, attempts, DLQ/dead status) and `stream_event`+`stream_checkpoint` (Kinesis shape: monotonic sequence, event_id dedup) behind `Queue`/`Stream` interfaces (ADR-0004, internal/ingestion/queue.go, stream.go). Raw bytes land in `FilesystemRawStore` under `RAW_STORAGE_PATH/{tenant}/{env}/{source}/{date}/{key}` with SHA-256 manifests (internal/ingestion/rawstore.go; data/raw/ shows real e2e artifacts).
- **Channels**: pluggable adapter Registry with four SimulatorAdapters (sms/email/push/ivr, main.go:178-183); inbound channel callbacks via public webhook route.
- **LLM gateway**: provider Registry always containing an offline deterministic SimulatorProvider, plus AnthropicProvider only when ANTHROPIC_API_KEY set (main.go:233-237); tool calls restricted to a closed read-only typed registry built from the same stores the HTTP API uses (internal/llm/tools.go BuildRegistry).
- **External integrations**: connector registry with HMAC-signed public webhook receiver (`POST /api/v1/webhooks/{connectorId}`), SSRF-guarded outbound pulls (internal/ingestion/ssrf_guard.go), in-memory secrets store shared between connector wizard and webhook verifier (main.go:126-130). No real third-party SaaS calls anywhere — all adapters are simulators by design at RC [verified across channels/integrations/llm code].
- **Infra**: docker-compose only runs Postgres+Valkey for dev; production topology per ADR-0006/CDK stacks. Note: **Valkey is provisioned but no Redis client exists in go.mod** — cache layer is designed (ADR-003) but not yet wired into code [verified: grep of *.go finds only comments/in-process rate limiter].

## MODULES

### core-api-monolith — Go modular monolith (all domains)
purpose: every REST endpoint, background worker, and domain rule for the platform
path_prefixes: services/core-api/cmd/*, services/core-api/internal/*
key_files: cmd/server/main.go (composition root + all routes), cmd/migrate/main.go (+ bootstrap.go seed.go), internal/db/{db,context,url}.go, internal/httputil/httputil.go
entrypoints: `go run ./cmd/server` (:8080), `go run ./cmd/migrate up|seed|bootstrap-up`
responsibilities: DI of ~30 store/handler pairs; correlation middleware; dual-pool DB access; worker lifecycle
invariants: runtime DB roles are NOSUPERUSER NOBYPASSRLS; tenant context set ONLY via db.WithTenantContext after server-side membership resolution; module storage is private — cross-module access only via exported Store methods (ADR-0001)
pitfalls: net/http ServeMux pattern ambiguity — sibling `{id}/versions` vs top-level `{resource}-versions` collections (see main.go:462-483 comments); adding a route without updating packages/contracts breaks contract sync [inferred]
confidence: verified

### auth-rbac-audit — Identity, tenancy, RBAC, audit, PII
purpose: sessions (opaque bearer tokens, SHA-256-at-rest), Argon2id passwords, TOTP MFA, invite/verify/recover, tenant lifecycle, custom roles + granular permissions, hash-chained append-only audit log, PII masking-by-default
path_prefixes: services/core-api/internal/{auth,tenants,rbac,audit,pii}
key_files: internal/auth/token.go, password.go, totp.go, account_handler.go, security_handler.go; internal/rbac/store.go; internal/audit/store.go (chain verify at GET /api/v1/tenant/audit/verify); internal/pii/pii.go (MaskEmail/MaskPhone; authorization deliberately NOT this package's job)
entrypoints: routes main.go:267-311 (auth/*, platform-admin/tenants/*, tenant/users|roles|audit)
responsibilities: signup→tenant creation (ADR-005), invitations as the only seat-grant path, MFA enrollment/login, session listing/revocation, suspend/reactivate tenants, audit chain integrity
invariants: session token only ever hashed server-side; PII reveal requires customers.read_pii permission AND is audited (POST /customers/{id}/reveal-pii); employees cannot self-register into existing tenants
pitfalls: superuser bypasses RLS regardless of FORCE — never point DATABASE_URL at the migration role (.env.example warnings)
confidence: verified

### data-pipeline — Connectors, ingestion, mapping, quality, identity resolution
purpose: get external telecom data in, map to canonical schema, quarantine bad rows, score quality, resolve duplicate identities
path_prefixes: services/core-api/internal/{integrations,ingestion,mapping,dataquality,identity,telecom/simulator}
key_files: internal/ingestion/{batch,api_pull,webhook,stream,worker,queue,rawstore,idempotency,retention,ssrf_guard}.go; internal/mapping/engine.go + engine_domains.go (8 source domains); internal/identity/{matching,merge,levenshtein}.go; internal/dataquality/{scores,detect via handler}.go; internal/telecom/simulator/generator.go (proven at 1M profiles)
entrypoints: POST integrations/{id}/batch|pull, public POST /api/v1/webhooks/{connectorId}, mapping dry-run/run, identity run-matching
responsibilities: idempotent batch/API/webhook/stream ingestion with DLQ + replay; versioned field mappings with dry-run; golden-record candidate preview/approve/reject with reversible merges; trust-rank policies per source; lineage graph
invariants: duplicate/replayed input is idempotent; malformed rows quarantine, never poison a run; a job without resolvable tenant is hard failure (ADR-002 §3)
pitfalls: SSRF guard is load-bearing for api_pull — do not bypass; simulator wipe is destructive (dedicated wipe.go + permission)
confidence: verified

### customer360 — Customer 360 + features
purpose: unified person view (accounts/subscriptions/usage/billing/network/interactions/consent/campaign history) and the windowed feature platform feeding models/decisions
path_prefixes: services/core-api/internal/{customer360,features}
key_files: internal/customer360/store.go; internal/features/{compute,snapshot}.go (compute_key closed registry; FilesystemSnapshotStore stands in for S3 Parquet)
entrypoints: GET customers/{id}, POST customers/{id}/reveal-pii, features definitions/recompute/values/snapshot
responsibilities: masked-by-default reads; leakage-safe windowed features with freshness flags; parity + leakage tests exist (features/parity_test.go, leakage_test.go)
invariants: reveal=false paths are what agents/AI see (llm/tools.go enforces); feature freshness degradation must surface, not fail (decisions/store.go buildContextSnapshot)
pitfalls: snapshot store is filesystem-local — multi-instance prod needs EFS (wired in CDK platform-stack.ts) 
confidence: verified

### audience-governance — Segments, offers, consent, approvals
purpose: rule-builder segments (AST → SQL, safelisted predicates), product catalog vs CVM offers, consent/contact-policy engine with suppressions, configurable separation-of-duties approval workflows
path_prefixes: services/core-api/internal/{segments,offers,consent,approvals}
key_files: internal/segments/{ast,translate,explain,drift}.go; internal/offers/{catalog,validate}.go; internal/consent/{evaluate,policy}.go; internal/approvals/store.go + notify.go
entrypoints: segments create/version/publish/preview/materialize/explain; offers versions/publish/submit-approval; consent events/policy/suppression; approvals requests/{id}/decide
invariants: segment attributes validated against closed Go registries before SQL construction — never dynamic column input (ast.go attributeFields); offer publish can require approval gate (offers/approval_gate_test.go); campaign dispatch always re-evaluates consent
pitfalls: segment SQL translation changes must keep explain-per-predicate parity (translate_test/explain_test)
confidence: verified

### activation — Campaigns, journeys, channels, experiments
purpose: versioned campaigns with lifecycle (draft→validating→awaiting approval→running→completed/killed) + kill switch; event-driven journey DAGs with wait/split/goal nodes; channel adapters; A/B/control experiments with incremental attribution
path_prefixes: services/core-api/internal/{campaigns,journeys,channels,experiments}
key_files: internal/campaigns/{execution,ops}.go; internal/journeys/{dag,execution,worker}.go; internal/channels/{registry,sms,callback,retry}.go; internal/experiments/stats.go + result.go
entrypoints: campaigns start/pause/resume/kill/dispatches; journeys trigger-run/steps/kill; channels config/disable/callback; experiments start/complete/result
invariants: journey split outcomes are pure functions of (runID,personID)+branches — deterministic on replay, no assignment table (dag.go SplitBranch comment); kill switch must stop dispatch blast-radius visibly
pitfalls: e2e suite is concurrency-flaky around heavy mutations (see TESTS/GIT LESSONS)
confidence: verified

### decision-intelligence — Analytics, models, decisions, opportunities, alerts
purpose: KPI semantic layer with A/B/C causal rigor grades; model registry/lifecycle/templates/monitoring; deterministic real-time NBA-NBO decision API with full trace; opportunity scout drafting; anomaly alerts with RCA assist; executive scorecard
path_prefixes: services/core-api/internal/{analytics,models,decisions,opportunities,alerts,executive,ops}
key_files: internal/models/{templates,studio,scoring,monitoring_compatibility,ml_client,worker}.go; internal/decisions/store.go (snapshot→policy→candidates→exclusions→scoring→arbitration→trace); internal/alerts/{detect,rca}.go; internal/opportunities/scout.go
entrypoints: analytics metrics/{key}; model-versions promote/score/monitor; POST tenant/decisions (real-time); opportunities scout; alerts detect
invariants: real-time decision NEVER depends on an LLM (RELEASE_NOTES.md); missing feature values degrade gracefully with trace chips, never fatal; model monitoring at 1M population uses bounded deterministic sampling (migration 0036 + monitoring_compatibility.go)
pitfalls: arbitration ordering is behavior — nil model versions have dedicated tests (nil_model_versions_test.go)
confidence: verified

### llm-gateway — Governed agentic layer
purpose: LLM conversations (converse), per-tenant AI policy (allowed models pinned to simulator by default), typed read-only tool registry, redaction before provider calls, alert/RCA/campaign-architect drafting
path_prefixes: services/core-api/internal/llm
key_files: tools.go (BuildRegistry), runtime.go, redact.go, anthropic.go, simulator.go, registry.go
entrypoints: POST ai/converse, GET/PUT ai/policy
invariants: tools expose only the same masked/read paths as HTTP APIs (reveal=false hardcoded, tools.go comment); no arbitrary SQL/shell tools; adversarial test suite guards this (eval_test, redact_test, alert_tool_test)
confidence: verified

### privacy-ops — DSAR, retention, ops console
purpose: DSAR export/anonymization (real anonymization, not row deletion), retention sweeps, operations snapshot (queue depth, DLQ replay, decision latency, journey lag, channel errors)
path_prefixes: services/core-api/internal/{dsar,retention,ops}
key_files: dsar/store.go, retention/worker.go, ops/handler.go
entrypoints: dsar requests CRUD, ops/snapshot, ops/dead-messages/{id}/replay
confidence: verified

### ml-service — Python training/scoring sidecar
purpose: leakage-safe windowed training (churn classification, CLV regression, propensity/NBO with productCategory labels), scoring, driver explanations, segment metrics, artifact persistence
path_prefixes: services/ml/app/*, services/ml/tests/*
key_files: app/main.py (TrainRequest/ScoreRequest pydantic contracts), features.py, training.py, artifacts.py, db.py
entrypoints: uvicorn app.main:app :8090 (Makefile dev)
responsibilities: pure compute; returns metrics/artifactRef; Go owns all registry state
invariants: observationWindowDays+labelWindowDays must be provided together (model_validator main.py:77-81); artifact writes are local-dir stand-in for S3
pitfalls: Dockerfile needs libgomp1 for lightgbm (fixed 7423f04)
confidence: verified

### web-console — Next.js app (marketing + auth + console)
purpose: bilingual (en/ar RTL) public site, auth screens, and the full operator console (~74 routes)
path_prefixes: apps/web/src/app/(marketing|(auth|protected))/[locale]/*, apps/web/src/lib/*, apps/web/src/proxy.ts
key_files: src/lib/guard.ts (server-side enforcement), src/lib/redirectUrl.ts (proxy-safe redirects), src/proxy.ts (locale negotiation), navItems.ts (grouped IA)
entrypoints: `next dev/build/start` :3000
responsibilities: server components fetch core-api via lib clients using session bearer token; form actions POST then redirect via redirectUrl()
invariants: hidden navigation is not authorization — requireSession on every protected page; NEXT_PUBLIC_APP_URL must be baked as build arg for canonical/SEO + redirect base (7423f04)
pitfalls: request.url origin is localhost under `next start` behind proxies — never build redirect URLs from it (99-file lesson)
confidence: verified

### packages — Shared frontend libraries
purpose: @telvora/ui (27 components incl. DecisionTrace, AuditLogRow, ConsentStatusPill), design-tokens (tokens.css), i18n (en.ts/ar.ts dictionaries), contracts (generated route list + OpenAPI)
path_prefixes: packages/{ui,design-tokens,i18n,contracts}/src
key_files: packages/contracts/src/core-api-routes.ts (generated), openapi/{core-api,ml}.openapi.json
confidence: strongly_inferred (ui/i18n internals not exhaustively read)

### e2e-infra — Playwright suite + AWS CDK + pipelines
purpose: black-box flows against running stack (EN+AR browser locales); IaC + CI/CD
path_prefixes: e2e/tests/*.spec.ts (38 files), infra/cdk/{lib,scripts}, .github/workflows
key_files: playwright.config.ts (two locale projects, webServer autostart), infra/cdk/lib/platform-stack.ts (Fargate web/core/ml, EFS access points, MigrationTask `/migrate bootstrap-up` barrier at line ~479-486), ci.yml (three jobs, live Postgres services, restricted-role test runs), deploy.yml (OIDC, SHA-tagged immutable images)
confidence: verified

## FLOWS

### Self-service signup → first Tenant Admin
trigger: visitor submits POST /api/v1/auth/signup {organizationName, ownerEmail} (public)
steps:
1. Rate-limited 5/hr/IP (reused leads.RateLimiter, ADR-0005)
2. CreateTenant with slug derived from org name + collision suffix; environment_label forced "sandbox"
3. Issue single-use invite account token bound to tenant-admin role; email invite link
4. Visitor lands on /invite/[token]; AcceptInvite sets password, verifies email, activates membership — zero new tables/tokens
files: internal/tenants/handler.go Signup, internal/auth/account_handler.go AcceptInvite, docs/adr/0005
confidence: verified

### Batch ingestion → canonical model
trigger: POST /api/v1/tenant/integrations/{id}/batch (or pull/webhook/stream)
steps:
1. Handler validates connector + permission; raw payload → FilesystemRawStore with SHA-256 manifest
2. Enqueue job on PostgresQueue (queue_message) with serialized tenant_id
3. Worker dequeues under telvora_worker pool; re-establishes tenant context; batch processor parses CSV/JSON
4. Mapping engine applies activated mapping version → canonical tables; failures → quarantine table
5. Data-quality detect/scores + lineage updated; incidents listed for remediation
files: internal/ingestion/{handler,worker,batch,rawstore}.go, internal/mapping/engine.go, internal/dataquality/
confidence: verified

### Real-time decision (NBA-NBO)
trigger: POST /api/v1/tenant/decisions {personId, ...} (authenticated, low-latency path)
steps:
1. Resolve tenant/person; build ContextSnapshot from feature values (degrades to stale/error chips, never fails)
2. Load eligible published offer versions; apply consent/suppression exclusions
3. Score candidates via deployed model versions (deterministic, no LLM); arbitrate winner
4. Persist decision with full trace (excluded candidates + versions kept); return recommendation
files: internal/decisions/store.go, handler.go:98; migration 0028_decision_engine
confidence: verified (store read; latency SLO claims from RELEASE_NOTES trusted as recorded measurements)

### Model training lifecycle (Go↔Python)
trigger: model version created (optionally from template) → submit-approval → promote → train/score via ML_SERVICE_URL
steps:
1. core-api resolves training population via segments.EvaluateVersion
2. HTTPMLClient POSTs /train {tenantId, modelVersionId, personIds, algorithm, taskType, windows, featureNames}
3. ml computes leakage-safe features from same Postgres (RLS-scoped), trains, writes artifact to local artifact dir, returns metrics/explanations
4. core-api persists metrics on model_version; worker sweeps drift/performance every 5min calling ml
files: internal/models/{ml_client,store,worker}.go, services/ml/app/main.py
confidence: verified

### Governed campaign execution
trigger: campaign start after validation + approval gate
steps:
1. Materialize segment members; consent evaluate per person/channel
2. Experiment bucketing assigns treatment/control (deterministic hash)
3. Dispatch via channel Registry adapter; callbacks recorded via public channel webhook
4. Kill/pause/resume manage runs; results computed as incremental value vs control
files: internal/campaigns/execution.go, internal/experiments/stats.go, internal/channels/registry.go
confidence: strongly_inferred (execution.go not fully read)

### Journey execution
trigger: TriggerRun or event_trigger node match; waits resumed by 2s scheduler worker
steps:
1. Run created; steps persisted per node traversal
2. Split nodes re-derive branch from (runID,personID) deterministically
3. Channel actions dispatch; goal node terminates; kill supported
files: internal/journeys/{dag,execution,worker}.go
confidence: strongly_inferred

### LLM converse (agentic draft)
trigger: POST /api/v1/tenant/ai/converse
steps:
1. Policy check (tenant's allowed_models; default pins offline SimulatorProvider)
2. Runtime lets model call closed read-only tool registry (permission checked per tool)
3. Redaction pass before external providers; conversation + tool calls persisted for audit
files: internal/llm/{runtime,tools,redact}.go
confidence: strongly_inferred

## APIS

~201 routes registered in services/core-api/cmd/server/main.go (grep count), mirrored in packages/contracts/src/core-api-routes.ts. Conventions: `/api/v1/...`; method-patterned ServeMux; `tenant` prefix = session-authenticated + RLS-scoped; `platform-admin` prefix = platform role; plural nouns, `{id}` path params, verb subresources (`/validate`, `/dry-run`, `/submit-approval`, `/promote`, `/kill`); two public unauthenticated endpoints use HMAC signatures instead of sessions (webhooks). Representatives:

| method | route | handler file:symbol | auth | notes |
|---|---|---|---|---|
| GET | /healthz | internal/health/health.go:Handler | none | version+buildSha |
| POST | /api/v1/leads | internal/leads/handler.go:Submit | rate-limited public | contact form capture |
| POST | /api/v1/auth/login | internal/auth/handler.go:Login | public | may require MFA verify step |
| POST | /api/v1/auth/signup | internal/tenants/handler.go:Signup | public, IP-limited | ADR-0005 |
| POST | /api/v1/platform-admin/tenants | internal/tenants/handler.go:CreateTenant | platform admin | suspend/reactivate siblings |
| PATCH | /api/v1/tenant/roles/{id}/permissions | internal/rbac/handler.go:UpdateRolePermissions | session+perm | granular perms |
| POST | /api/v1/webhooks/{connectorId} | internal/ingestion/handler.go:ReceiveWebhook | HMAC secret | public by design |
| POST | /api/v1/webhooks/channels/{providerRef} | internal/channels/handler.go:ReceiveCallback | HMAC secret | delivery receipts |
| POST | /api/v1/tenant/customers/{id}/reveal-pii | internal/customer360/handler.go:RevealPII | customers.read_pii | audited |
| POST | /api/v1/tenant/segments/{id}/materialize | internal/segments/handler.go:Materialize | session+perm | AST→SQL |
| POST | /api/v1/tenant/campaigns/runs/{runId}/kill | internal/campaigns/handler.go:Kill | session+perm | blast radius surfaced |
| POST | /api/v1/tenant/decisions | internal/decisions/handler.go:CreateDecision | session+perm | real-time NBA |
| POST | /api/v1/tenant/model-versions/{versionId}/promote | internal/models/handler.go:Promote | session+perm | lifecycle gate |
| POST | /api/v1/tenant/ai/converse | internal/llm/handler.go:Converse | session+policy | governed tools |

## DATABASE

Engine: PostgreSQL 18 everywhere (docker-compose, CI, prod RDS; uuidv7() PK default relies on PG18 builtin — reason ADR-0006 picks RDS over Aurora). 36 numbered migrations ×(up/down) under services/core-api/db/migrations (0001_platform_leads … 0036_model_monitoring_compatibility) applied by golang-migrate via elevated role only.

Notable entities WITH MEANING:
- tenants / tenant_memberships / users / roles / permissions — pooled tenancy roots; memberships resolve server-side tenant context (migration 0002/0004/0005)
- audit_events — append-only hash chain; VerifyChain endpoint proves integrity (B09, commit b904135)
- person / identity / customer_account / subscription / usage / billing / consent / interaction — canonical telecom model (B10, migration 0008). person holds NO PII directly; identifiers live in temporal identity rows (valid_from/valid_to, unique active value index) because MSISDNs recycle
- integration_connector / mapping_version / quarantine / queue_message / stream_event / stream_checkpoint — ingestion runtime; queue_message implements SQS semantics (visible_at, attempts, dead) and has the single cross-tenant RLS policy scoped to `current_user='telvora_worker'` (migration 0012)
- segment(_version)/members, offer/product(_version), consent_event/policy/suppression, approval_workflow/request — audience & governance
- campaign(_version/run/dispatch), journey(_version/run/step), experiment/arm, channel_config — activation
- kpi definitions/views (B27 semantic layer), model_registry/model_version/scores/monitoring_runs, studio_runs (B28/B32/B34), decision + trace jsonb (B30), llm_conversation/policy (B31), opportunity, alert, dsar_request
- business_definitions (B34... actually 0034) — tenant churn/ARPU/conversion windows

RLS/policies: every tenant-owned table gets ENABLE + **FORCE** ROW LEVEL SECURITY with policy `tenant_id = NULLIF(current_setting('app.tenant_id', true))::uuid` (pattern established by fix migration 0006 after an empty-string cast bug). App sets GUC per transaction via set_config(...,true) (internal/db/context.go). Roles: telvora (superuser, migrations only), telvora_app (runtime), telvora_worker (queue-only cross-tenant) — db/init/01-app-role.sql. Migration 0035 adds partition RLS hardening (uncommitted). Isolation is regression-tested per-module (*rls_test.go files) against live Postgres.

Vector stores: none. Caches: Valkey container provisioned; no client wired yet (see Risks).

## TESTS

- Go: `cd services/core-api && TEST_DATABASE_URL=... go test ./...` — 149 test files; every module carries handler/store tests PLUS a dedicated rls_test.go negative cross-tenant suite; special suites: ssrf_guard, idempotency/DLQ/retention (ingestion), dag/execution (journeys), stats (experiments), parity/leakage (features), adversarial LLM eval/redact. CI spins postgres:18 service, creates restricted roles, migrates, then tests under the restricted role (.github/workflows/ci.yml).
- Python: `.venv/bin/pytest -q` in services/ml (tests: training, features, artifacts, health, db config, OpenAPI contract, API validation).
- E2E: `pnpm --filter @telvora/e2e test` — 38 specs (auth, tenant-lifecycle, ingestion, mapping, identity, segments, offers, consent, approvals, campaigns, journeys, experiments, models, model-studio, decisions, opportunities, alerts, ai, ops-console, executive-home, privacy-security-hardening, seo, landing, self-service-signup…) running against dev stack in chromium-en + chromium-ar.
- Load: `make test-load` — k6 mixed-load + dedicated tenant-isolation k6 suite (load/).
- Gates: `make verify` = prettier format + eslint + tsc --noEmit + pnpm test + builds + gofmt/go vet + ruff.
Coverage mapping: each B-phase maps 1:1 to module packages + e2e spec names; known gap: full-suite parallel runs flake on shared-state heavy mutations (267/280 at 4 workers documented in docs/UX_REDESIGN_AUDIT.md tail).

## GIT LESSONS

- `49ee13f` — Route-conflict protocol: when a new phase's spec conflicts with a completed phase's route ownership, resolve the contradiction immediately (moved identity-resolution under /app/customers) instead of shipping compatibility shims. Protocol text lives in AGENT_BUILD_PROTOCOL.md.
- `7423f04` — Three production-deploy bugs worth remembering forever: (1) Next.js `request.url` origin is http://localhost:3000 under `next start` regardless of Host/X-Forwarded-Host — all 223 POST-redirect constructions across 99 handlers were centralized into src/lib/redirectUrl.ts resolving against NEXT_PUBLIC_APP_URL; (2) NEXT_PUBLIC_* vars inline at BUILD time — wire them as Docker build args or SEO/canonical bakes localhost; (3) python-slim images lack libgomp1 which LightGBM loads at import-runtime (pip install passes, container crashes); (4) the migrate image must ship db/migrations SQL, not just binaries.
- ServeMux ambiguity (documented in main.go:462-483 comments, learned in B28): Go rejects registering `models/{id}/versions` alongside `models/versions/{id}` — convention adopted: top-level `{resource}-versions`, `{resource}-runs` collections (journeys did this first).
- Migration 0006 (fix_rls_empty_string_cast): RLS policies casting `current_setting(...)` to uuid must wrap in NULLIF(x,'') or unset-GUC becomes a cast error; pattern made mandatory for all later migrations (0008 header states it).
- Migration 0010 (foreign_key_delete_indexes): B11 retrofit taught "add FK-column-leading indexes at table creation," encoded as a rule in ADR-0004.
- `b904135` (B09): audit hash-chain + PII masking built BEFORE any PII-bearing table existed — "define the shape now, wire real data later" pattern (pii.go package doc).
- Dangerous areas: simulator wipe + tenant suspend (destructive, permission-gated); campaign/journey kill switches; PII reveal; DLQ replay (ops); segment materialize cost at scale.
- Reverted approaches: none found — zero revert commits in history (`git log --grep revert` empty). Corrections happen as forward fixes (0006, 0010, 49ee13f).
- E2E flakiness is environmental, not code: heavy-mutation specs share one admin account + one local PG; documented with evidence in UX_REDESIGN_AUDIT.md final-regression section.

## DECISIONS

- Modular monolith, not microservices — spec warned against premature decomposition; only ml split out for runtime needs; workers share the Go tree — docs/adr/0001.
- Pooled tenancy + FORCE RLS as primary control, defended in depth (middleware-set GUC, worker role trust boundary, tenant-scoped everything, per-phase negative tests) — docs/adr/0002, db/init/01-app-role.sql.
- Storage split with deliberate omissions (no ClickHouse/Snowflake; Athena-over-S3 planned, not built locally; Valkey disposable cache) — docs/adr/0003.
- Honest local adapters over emulators: RawStore/Queue/Stream interfaces with filesystem/Postgres implementations matching S3/SQS/Kinesis contracts exactly, so prod swap is a config-level adapter addition — docs/adr/0004.
- Self-service signup reuses invite-accept verbatim (password collected on accept screen, sandbox-only label, reused rate limiter) rather than inventing a second verification primitive — docs/adr/0005.
- Production topology honest about actual implementation: RDS (not Aurora) because PG18 uuidv7 + CDK engine gap; EFS for filesystem adapters instead of pretending S3 adapters exist; CFN custom-resource migration barrier before rollout; OIDC + immutable SHA tags — docs/adr/0006, infra/cdk/lib/platform-stack.ts.
- Deterministic real-time path: LLMs never in the decision loop; they draft/explain only, behind typed read-only tools + per-tenant policy — RELEASE_NOTES.md, internal/llm/tools.go.
- Phase-ordered agent build (B00→B41, exit-gated, contradiction-resolution rule) as the execution contract — AGENT_BUILD_PROTOCOL.md.

## RISKS & TECH DEBT

- ~237-file dirty tree on master: the entire post-RC hardening + AWS deploy wave is UNCOMMITTED (git status). One careless checkout loses ADR-0006/CDK/migrations 0035-0036 work. Commit urgency: high.
- Stray `--full-page` PNG (28KB screenshot) committed to working-tree root — debris; also giant planning artifacts (CVM spec PDF/DOCX ~2.5MB, BUILD_STATUS.md 465KB) tracked at repo root [uncertain whether intentional].
- Valkey provisioned in compose/env but unused by any code (no redis client in go.mod) — either wire caching (ADR-003 intent) or drop the container; today it's decorative.
- In-memory constructs that break horizontal scale: leads/signup rate limiter (per-IP, in-process, admitted in ADR-0005), ConsoleNotifier, in-memory secrets store (main.go:130), filesystem raw/snapshot/artifact stores — all fine on one Fargate task, all wrong at >1 instance unless EFS-backed and single-task-constrained [CDK wires EFS; autoscaling limits unverified].
- E2E concurrency flakiness on shared fixtures (documented 13/280 failures) — needs per-worker tenants/accounts or seeded isolation before CI-enforced full parallel runs.
- Single-process workers: ingestion/journey/model/retention workers are goroutines of the API binary (ADR-0001 said separately deployable `cmd/worker-*` binaries — never materialized; scaling workers means scaling the whole API) [verified: only cmd/server and cmd/migrate exist].
- Auth/session store is Postgres-only with opaque tokens; no rotation/sliding-expiry evidence reviewed [uncertain].
- Anthropic provider hardcodes "claude-sonnet-5" model string (main.go:235) — will rot.
- `--full-page` filename and `03_DESIGN_SYSTEM.md` living at repo root while also referenced as docs/03_DESIGN_SYSTEM.md (docs/ contains its own copy) — duplication risk between root copy (58KB, newer) and docs copy [verified both exist].
- ML port mismatch traps: Makefile/.env use 8090, main.go default ML_SERVICE_URL=8001 — works only when env is set (it is in dev scripts) [verified strings].
- No vector store/search beyond Postgres ILIKE-style search endpoints [inferred]; global search page exists (/app/search) backed by src/lib/search.ts — implementation depth unverified.

## UNCERTAIN

- Whether Athena/S3/Parquet historical-analytics path exists at all in code — ADR-0003 plans it; I found no Athena client anywhere; likely still future work.
- Exact content of ~20 of the 30 Go domain packages was sampled, not exhaustively read (campaigns execution, ops, dsar, executive internals inferred from handlers/tests/comments).
- Whether CI actually runs e2e (ci.yml head shows web/core-api/ml jobs; e2e job presence unverified past first 90 lines).
- packages/ui component completeness vs DESIGN_SYSTEM spec; i18n dictionary parity EN/AR not audited.
- Root `--full-page` PNG provenance (likely a stray Playwright/screenshot export during redesign QA).
- Whether BUILD_STATUS.md's claim TS 7.0.2 vs package.json typescript 6.0.3 reflects a doc typo or a toolchain nuance (package.json is authoritative for installs).
- Actual measured prod behavior: ADR-0006 itself admits "local synthesis does not constitute proof of live AWS behavior"; deployment drill status unknown.
