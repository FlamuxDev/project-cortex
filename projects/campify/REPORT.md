# CORTEX REPORT — Campify

## META
project_id: campify
root: /home/aboud/Dev/Campify
kind: pnpm monorepo, multi-tenant B2B SaaS (marketing campaign manager), modular monolith
languages: TypeScript (strict, ESM), SQL (hand-written reviewable migrations), Node >=22
frameworks: Next.js 15 + React 19 (web), Fastify 5 (api), zod (validation), pg (driver; raw SQL, NOT an ORM despite ADR-0006 naming Drizzle — see UNCERTAIN)
package_managers: pnpm@9.15.4 (workspace: apps/*, packages/*)
test_frameworks: vitest (projects: unit, integration, tenancy, contract, e2e) + @playwright/test (browser suite, chromium only)
deployment: production at campify.ai [inferred from docs/engineering/LAUNCH_READINESS.md + PROGRESS.md M14: `campify.ai`, 13.235.74.89]; CI = .github/workflows/verify.yml runs `pnpm verify` (all gates) on every push/PR; local dev DB = embedded-postgres 18.4 on port 5434, no Docker

## OVERVIEW

Campify is an Arabic-first (default locale `ar`, RTL; `en` supported), multi-tenant B2B SaaS for planning and executing multi-channel marketing campaigns — WhatsApp, Email, SMS — from audience import, through segmentation and content authoring, to delivery with consent enforcement and measured revenue (README.md; CLAUDE.md). Target customer is the Arabic-first SMB; the product deliberately ships a native CRM rather than assuming customers own one (ADR-0013). Users are workspace members in six roles (`owner|admin|marketer|analyst|sales|viewer`, packages/core/src/identity/rbac.ts:19).

It is built as three processes over one PostgreSQL database: `apps/web` (Next.js — public indexable marketing site `(public)` + private never-indexed app `(app)`, acting as a same-origin BFF), `apps/api` (Fastify versioned `/v1` REST API, webhooks, API keys), and `apps/worker` (polling delivery/journey/webhook engine). Domain logic lives in framework-free `packages/core`; persistence in `packages/db` behind a tenant-scoped helper; env in `packages/config`; providers behind ports implemented by `packages/adapters/*` (EXECUTION_SPEC.md §4). The defining engineering property is defense-in-depth tenant isolation: Postgres RLS (`ENABLE`+`FORCE`) keyed on `current_setting('app.workspace_id')`, app connects as a non-superuser `NOBYPASSRLS` role, all queries inside `withTenant()`, and every tenant table attacked behaviourally by a dedicated test project (packages/db/test/, ADR-0003/0010).

Development history is unusually disciplined: every change cites PRD requirement IDs, gates must pass before any commit (`pnpm verify`), each milestone got an independent adversarial security/quality review recorded in docs/engineering/PROGRESS.md, and the product was launched to production after milestone M14 (LAUNCH_READINESS.md). Roughly 58k LOC of TS/TSX across apps+packages (measured).

## ARCHITECTURE

Dependency direction `apps/* → core → db → config`, arrows enforced by ESLint; `core` depends only on typed ports (packages/core/src/ports/index.ts), adapters injected at process start in `apps/*/src/container.ts`.

Runtime components:
- **apps/web** (Next.js): route groups `(public)` (SSG marketing, full metadata, sitemap.ts/robots.ts) and `(app)` (private shell). Middleware validates sessions by calling `GET /v1/me` and fails closed (apps/web/src/middleware.ts:53). All mutations are Next Server Actions (apps/web/src/lib/actions.ts) or two thin proxies `/api/login`, `/api/signup` (BFF pattern, ADR-0011). Sets `X-Robots-Tag: noindex` on all /app responses.
- **apps/api** (Fastify): builds the whole HTTP surface in apps/api/src/app.ts (~1400 lines): zod boundary parsing, typed domain-error → status mapping, correlation ids (always server-generated), one access-log line per request logging ROUTE PATTERN not resolved path, raw-body capture for HMAC webhook verification, per-route body limits with an unauthenticated pre-read guard on import routes, fixed-window in-process rate limiter (apps/api/src/rateLimit.ts) keyed user>apiKey>ip.
- **apps/worker** (node process): 5s tick loop with five independent polls (apps/worker/src/main.ts): campaign starts (`due_campaign_starts()` SECURITY DEFINER discovery → engine transition + message materialization), message dispatch (`QueuePort.claim` → `dispatch()`), journey entries (`due_journey_entries()`), journey steps (`executeStep`), webhook deliveries (`dispatchWebhookDelivery`). Cross-tenant discovery uses narrow SECURITY DEFINER functions returning bare ids only (packages/adapters/queue-inprocess/src/index.ts:31).
- **PostgreSQL** (embedded-postgres locally, port 5434): system of record AND the queue (tables double as job queues; claim = `for update skip locked`). Roles: `postgres` superuser (migrations/init only) vs `campify_app` non-superuser NOBYPASSRLS (app traffic) — created by scripts/db.mjs:162.
- **Queues**: none external. Three claim-only port interfaces (`QueuePort`, `JourneyQueuePort`, `WebhookQueuePort`, ports/index.ts:125-166) backed by `queue-inprocess` adapter polling the tables themselves; 5-min visibility timeout makes a crashed worker's claim re-claimable (at-least-once).
- **External integrations**: Resend (email send + inbound Svix-signed delivery webhooks), Gemini (AI Copilot), arbitrary customer URLs (outbound webhooks via `webhook-http` adapter). All gated on credentials being present — absent config falls back to fakes that do zero network I/O (packages/adapters/fake/src/index.ts; packages/config/src/index.ts:37-71). SMS/WhatsApp remain fake pending decision D3.

Background jobs live entirely in the worker's tick loop; there is no cron scheduler beyond it.

## MODULES

### config — validated environment
purpose: the ONLY reader of process.env; zod-validated, fails boot loudly.
path_prefixes: packages/config
key_files: packages/config/src/index.ts
entrypoints: getConfig() called by apps/*/src/container.ts and server mains
responsibilities: parse env once; missing/invalid ⇒ exit non-zero listing ALL problems.
invariants: NODE_ENV required with NO default (a defaulted deploy once booted fail-open — token echo + non-Secure cookie, commit 578b127); RESEND_API_KEY+EMAIL_FROM required together or fake email stays live; RESEND_WEBHOOK_SECRET absent ⇒ inbound webhook refuses everything.
pitfalls: adding env reads anywhere else breaks SEC-004 and the audit:security gate.
confidence: verified

### db — schema, RLS policies, tenant data access
purpose: migrations, RLS policies, and the `withTenant` boundary around every tenant query.
path_prefixes: packages/db
key_files: packages/db/src/tenant.ts, packages/db/migrations/ (39 numbered pairs + 0014_suppression_backfill_via_domain.mjs code migration), scripts/db.mjs, packages/db/test/*.tenancy.test.ts
entrypoints: getPool(), withTenant(), withoutTenantScopeForPlatformAdmin(); `pnpm db:up|migrate|reset|verify`
responsibilities: transaction-scoped tenant context; schema evolution with mandatory .down.sql; invariant verification (`db:verify` asserts FORCE RLS everywhere, app role lacks BYPASSRLS, down files exist).
invariants: every tenant table has workspace_id + ENABLE/FORCE RLS + policy on `current_setting('app.workspace_id')`; tenant set via `select set_config('app.workspace_id',$1,true)` (SET LOCAL takes no binds — interpolation would be injection); unset tenant ERRORS (fail closed, never default); every FK into a tenant table composite on (workspace_id,id) (ADR-0010); migrations immutable once committed.
pitfalls: superuser bypasses RLS even with FORCE; `ON DELETE CASCADE`/FK checks run with RLS disabled — single-column FKs were a real cross-tenant write hole (commit 1e7ead5); concurrent queries on one TenantClient are deprecated by pg — keep sequential (apps/api/src/app.ts:930).
confidence: verified

### identity — users, sessions, workspaces, RBAC
purpose: signup/verify/login/logout, sessions, memberships, invitations, the RBAC matrix.
path_prefixes: packages/core/src/identity, apps/api/src/app.ts (auth+workspace routes)
key_files: packages/core/src/identity/service.ts, rbac.ts, password.ts (scrypt), emails.ts; apps/api/src/app.ts
entrypoints: POST /v1/auth/*, /v1/me, /v1/workspaces, invitations/members routes; assertCan()/can() used by every handler
responsibilities: opaque server-side session tokens (hash-stored), scrypt passwords, six-role × permission matrix asserted cell-by-cell against PRD §20.3; invitation tokens bound to accepting user's address, `on conflict do nothing` so an invitation can never mutate an existing membership.
invariants: only an owner may grant/revoke owner (enforced in changeRole, removeMember AND inviteMember — partial hardening produced a takeover, commit ea32541); last-owner demotion guarded INSIDE the UPDATE/DELETE after `select … for update`; non-member sees 404 not 403 (workspace existence is a leak); verification/invite tokens never returned to callers in prod.
pitfalls: global tables (users/sessions) run outside tenant scope by design; auth throttles are tight (signup 5/min) and unauthenticated ones key on req.ip — bites any test minting many accounts (PROGRESS.md M18).
confidence: verified

### contacts — contact profiles, fields, tags, lists
purpose: canonical person record + custom fields/tags/lists, normalization of emails/phones.
path_prefixes: packages/core/src/contacts
key_files: packages/core/src/contacts/repository.ts, normalize.ts
entrypoints: /v1/workspaces/:id/contacts* routes; import commit path
responsibilities: create/get/delete/list console with paging; normalization (lowercase email, phone E.164-ish) feeding dedupe and suppression matching.
invariants: dedupe on normalized destination; deleteContact writes audit.
pitfalls: paging past page 1 requires `data:export` permission — deep paging IS an export (apps/api/src/app.ts:897).
confidence: verified

### consent — ledger, suppression, send gate
purpose: strict opt-in consent ledger + suppression list; THE gate every send passes.
path_prefixes: packages/core/src/consent
key_files: packages/core/src/consent/gate.ts, repository.ts; migrations 0003/0010/0012/0013
entrypoints: evaluateSendGate() (pure) called from checkSendAllowed() in dispatch; POST …/consent, POST …/suppressions
responsibilities: per-channel granted/withdrawn/pending/unknown; supersede trigger keeps one current row; suppression checked again at execution moment.
invariants: no bypass flag exists; relaxing policy is a legal/product decision, never code (ADR-0005); suppression evaluated BEFORE consent so unsubscribe beats a later re-grant; imported consent must carry explicit source+timestamp (import cannot fabricate).
pitfalls: consent_supersede's unique key was once occupiable by a foreign-tenant row (the ADR-0010 hole) leaving victims unable to record consent; writes serialized historically due to lock contention (commit 89b8ad2).
confidence: verified

### imports — CSV/XLSX dry-run then commit
purpose: two-phase import: parse/validate/dedupe into a persisted plan, preview it, then apply.
path_prefixes: packages/core/src/imports
key_files: packages/core/src/imports/sheet.ts, dryRun.ts, commit.ts
entrypoints: POST …/imports/preview, PUT …/imports/:jobId/mapping, POST …/imports/:jobId/commit
responsibilities: mapping suggestion + remap; row-level reject reasons; counts derived from stored rows so endpoints can't disagree (apps/api/src/app.ts:1063).
invariants: preview touches zero contacts; commit applies the previewed plan only; per-entry inflation caps and bounded columns (zip-bomb defenses, commits 063c501, fb73083).
pitfalls: 20 MB bodies parsed on the event loop — guarded pre-read + throttled (apps/api/src/app.ts:353); quadratic XLSX parsing was a real outage-class bug.
confidence: verified

### segments — AST compiled to parameterised SQL
purpose: dynamic/static audiences defined as JSON AST, compiled live with bind params only.
path_prefixes: packages/core/src/segments
key_files: packages/core/src/segments/ast.ts, compile.ts, repository.ts
entrypoints: POST …/segments(/preview|/:id/recount|/:id/snapshot); used by campaign audience + snapshot freeze
responsibilities: validate AST against closed field allow-list; live count/sample; static snapshots freeze member ids at launch (campaign approval, repeatable-read tx).
invariants: NO value from the definition is ever concatenated into SQL — hostile-input unit tested (compile.ts header); SQL is never persisted.
pitfalls: pathological definitions (199 `not_contains` leaves) ran 56s — statement_timeout (migration 0011) + per-route throttle cap the class (apps/api/src/app.ts:1207).
confidence: verified

### campaigns — campaign domain, state machine, audience, approval
purpose: lifecycle draft→in_review→scheduled→running… with version-bound four-eyes approval.
path_prefixes: packages/core/src/campaigns
key_files: packages/core/src/campaigns/state.ts, approval.ts, blockers.ts, configuration.ts, fingerprint.ts, objectives.ts, repository.ts
entrypoints: /v1/workspaces/:id/campaigns* (submit/approve/reject/withdraw/transition/audience/channels/tracking/duplicate/blockers/estimate)
responsibilities: explicit transition table transcribing PRD §7.2; approval certifies audience under repeatable read and freezes the active version; blockers computed for the UI.
invariants: engine transitions (`start`,`complete`,`fail`…) are UNREACHABLE over HTTP — actor defaults to 'api' so forgetting to say who is acting cannot start execution (state.ts:220); submitter cannot approve (four-eyes; no owner exemption until M18 made a members UI exist — PROGRESS.md); failed is recoverable via `fix`→draft, terminal statuses are completed/stopped only; edit allowed only in draft; scheduled/running/paused versions frozen.
pitfalls: a GENERIC transition route once could approve a campaign (commit fac3d6d) — transition-specific routes exist since; stop exists only from paused (deliberate two-step destructive action).
confidence: verified

### content — studio, versions, templates, A/B, AI copilot, personalization
purpose: channel content per campaign version; immutable append-only versions; variant allocation; AI suggestions with structural human-in-the-loop; {{token}} rendering.
path_prefixes: packages/core/src/content, packages/adapters/ai-gemini
key_files: packages/core/src/content/copilot.ts, personalization.ts, abTest.ts, preview.ts, repository.ts; packages/adapters/ai-gemini/src/prompt.ts
entrypoints: campaign sub-routes …/content*, /variants, /allocations, /ab-test, /preview, /ai/suggest|accept; renderContent() inside dispatch()
responsibilities: version history + restore; template application; A/B fingerprint where each field matters individually (commit 10f7a0d); prompt-injection boundary: instructions ONLY from closed AiTask set into systemInstruction, user brief travels as JSON data (prompt.ts).
invariants: `suggest()` writes nothing; nothing applies model output without a separate audited accept taking text as argument (copilot.ts — property of module shape, not a removable check); content_version immutability enforced by DB trigger (migration 0016/0020); missing-fallback token blanks rather than crashes at send time (submission-time blocker instead).
confidence: verified

### delivery — send pipeline, retries, quiet hours, provider events
purpose: turn a claimed message into a real send through every §13.3 control; ingest provider status.
path_prefixes: packages/core/src/delivery, migrations 0021/0030/0031/0032
key_files: packages/core/src/delivery/dispatch.ts, retry.ts, quietHours.ts, idempotency.ts, providerEventIngest.ts, repository.ts
entrypoints: worker tickDispatch → dispatch(); POST …/emergency-stops, GET …/messages, test-send/test-recipients/quiet-hours-override; POST /v1/providers/resend/webhook
responsibilities: order of gates: emergency stop → suppression → quiet hours → frequency cap → monthly quota → rate limit → resolve frozen content → personalize → port.send → classify transient/permanent → exponential backoff w/ jitter (MAX_ATTEMPTS); bounce/complaint ⇒ automatic suppression.
invariants: emergency stop and suppression re-checked AT EXECUTION (claim-time filtering insufficient); quiet hours before frequency cap (reservations commit immediately — don't spend caps on deferrals); quota lives HERE because campaigns, journey sends, and test sends converge on dispatch; idempotencyKey is `${message.id}:${attempt}` (retry may resend; duplicate claim collapses); quota-exceeded defers (allowance resets) while suppression fails permanently.
pitfalls: quiet-hours override set only by campaign:approve; test sends exempt from frequency/quota but NOT system rate limit; attribution anchor is messages.sent_at (commit cf88b83 fixed drift).
confidence: verified

### journeys — visual automation engine
purpose: publishable node graphs (wait/send/task/branch/webhook) with enrollment and step execution.
path_prefixes: packages/core/src/journeys
key_files: packages/core/src/journeys/graph.ts, enroll.ts, execute.ts, wait.ts, state.ts, repository.ts
entrypoints: /v1/workspaces/:id/journeys* (draft/graph/publish/pause/resume/enrollments); worker ticks enrollDueContacts + executeStep
responsibilities: immutable published versions (DB triggers journey_version_immutable/journey_graph_immutable); entry criteria polled; step rows claimed like messages; a Send node INSERTS a messages row — the SAME queue/guards as campaigns, never a parallel send path (execute.ts header).
invariants: paused/stopped journeys excluded at discovery AND re-checked at execution; wait steps reschedule via scheduled_at; webhook nodes reuse the outbound-webhook infrastructure.
pitfalls: journey-originated messages have no campaign — LEFT JOIN semantics; quiet_hours_override defaults false for them (dispatch.ts:101).
confidence: verified

### analytics — events, conversions, attribution, ROI, reports
purpose: API-key event ingestion, last-touch attribution, per-campaign reports + dashboard rollups.
path_prefixes: packages/core/src/analytics, packages/core/src/integrations/apiKeys.ts, apps/api/src/apiReadRoutes.ts
key_files: packages/core/src/analytics/attribution.ts, roi.ts, abtest.ts, repository.ts; apps/api/src/apiKeyAuth.ts; migrations 0024/0026/0035
entrypoints: POST …/events (Bearer API key), GET …/campaigns/:id/report(.csv), GET …/dashboard; partner read surface /v1/w/:id/{contacts,segments,campaigns,events,conversions} via requireApiKey
responsibilities: hash-only API keys (plaintext shown once); find_active_api_key SECURITY DEFINER lookup before tenant scope exists; conversion windowing vs most recent send; completeness flags — ROI WITHHELD, not guessed, when cost/revenue partial (§15.3); attribution model disclosed on every report.
invariants: attribution is last-touch in-campaign, explicitly labelled (D8 stand-in); usage_counters never decrease (DB function); workspace_plans revokes write from app role so no route can raise a ceiling (migration 0033/0036).
pitfalls: executiveDashboard is N+1 per campaign (ponytail-flagged, LAUNCH_READINESS §3).
confidence: verified

### sales-tasks — follow-up queue
purpose: tasks handed from campaigns/journeys to humans, assigned, tracked to outcome.
path_prefixes: packages/core/src/sales
key_files: packages/core/src/sales/state.ts, context.ts, repository.ts
entrypoints: /v1/workspaces/:id/sales-tasks* (assign/transition/notes); journey Task node creates them
responsibilities: explicit open→claimed→done/canceled style machine (no reopen row — unrequested); context assembly rolls contact+campaign history for the assignee.
invariants: transitions table-driven like campaigns; dashboard rollup aggregates.
pitfalls: independent-review defect pass was needed even here (commit 24d8656).
confidence: strongly_inferred

### crm — native companies/deals/pipeline
purpose: native CRM (ADR-0013): companies, deals on per-workspace pipelines, activity timeline.
path_prefixes: packages/core/src/crm
key_files: packages/core/src/crm/repository.ts; migrations 0034
entrypoints: /v1/workspaces/:id/crm/* (companies, deals, stage, outcome, activities, stages)
responsibilities: deals reference contacts (single identity record — never restates name/email); default pipeline seeded by seed_default_pipeline().
invariants: contacts stays the single source of person identity.
confidence: strongly_inferred

### plans — commercial limits
purpose: plan catalog + per-workspace overrides; atomic quota reservation for billed metrics.
path_prefixes: packages/core/src/plans, migrations 0033/0036/0037
key_files: packages/core/src/plans/repository.ts
entrypoints: reserveQuota/effectiveLimits called from dispatch + copilot metering; GET …/plan; platform_set_workspace_plan SECURITY DEFINER (operator-only, via `pnpm plan`)
responsibilities: null=unlimited convention; override-null=inherit-plan resolved once in effectiveLimits; monthly period windows; trial seats.
invariants: no payment gateway by decision — this protects margin only; ceilings changed only with database-owner access (deliberate posture, LAUNCH_READINESS §3).
confidence: verified

### webhooks — outbound subscriptions + inbound provider events
purpose: signed outbound event delivery to customer URLs; HMAC-verified inbound Resend events.
path_prefixes: packages/core/src/webhooks, packages/adapters/webhook-http, migrations 0029/0030
key_files: packages/core/src/webhooks/dispatch.ts, signing.ts, inboundSigning.ts, urlGuard.ts, repository.ts
entrypoints: /v1/workspaces/:id/webhook-subscriptions*, /webhook-deliveries*(redeliver); POST /v1/providers/resend/webhook
responsibilities: emission wired into 8 domain events; HMAC signing incl. replay bounding; SSRF-guarded URL validation (urlGuard); delivery queue with redeliver.
invariants: raw-body bytes preserved for signature verification (app.ts:335 replaces JSON parser); secret absent ⇒ refuse everything (lose feature, not control); subscription secrets plaintext (must be readable to HMAC — flagged debt).
pitfalls: ANY non-2xx retries all 5 attempts (deleted endpoint burns budget; ponytail-flagged in dispatch.ts).
confidence: verified

### api-app — HTTP plumbing (Fastify)
purpose: everything cross-cutting on the API: zod boundaries, error mapping, correlation ids, throttles, guards.
path_prefixes: apps/api/src (app.ts, rateLimit.ts, apiKeyAuth.ts, server.ts, container.ts)
key_files: apps/api/src/app.ts
entrypoints: buildApp(); server.ts binds API_PORT
responsibilities: see ARCHITECTURE; distinct client states for login failures; PG error codes mapped (40001→409 retry, timeouts→503, 23503→404 logged, 23505→409); driver errors logged structurally WITHOUT message/detail (PII).
invariants: correlation id always server-generated (client-supplied echoed separately — audit-log forgery otherwise); body limit 256KB globally, 20MB import-only with pre-read auth+membership guard.
pitfalls: rate limiter in-process (multiplies with N instances); authenticated throttles key on userId because BFF collapses IPs.
confidence: verified

### web-app — Next.js UI + BFF
purpose: public site, private app UI, server actions, i18n ar/en RTL.
path_prefixes: apps/web/src
key_files: apps/web/src/middleware.ts, lib/actions.ts, lib/api.ts, lib/i18n.ts, app/(public)/*, app/(app)/*
entrypoints: middleware (session gate + noindex); /api/login,/api/signup proxies; server actions for all mutations
responsibilities: session validated (not shape-checked) per navigation, failing closed; actions carry intent only — rules live in core/API; campaign builder tabs, segment builder, journey canvas, import wizard, team screen.
invariants: /app never indexable (edge header + middleware + robots + automated test, ADR-0009); tokens consumed then redirected away (Next serializes searchParams into RSC payload/history/Referer).
pitfalls: `?next` validated by origin comparison, never regex; waitForURL-before-click race pattern broke tests 3× (PROGRESS.md M15/M18).
confidence: verified

### worker — delivery engine process
purpose: all outbound side effects owned here; five polls per 5s tick.
path_prefixes: apps/worker/src
key_files: apps/worker/src/main.ts, container.ts
entrypoints: node apps/worker/dist/main.js
responsibilities: campaign starts, message dispatch, journey entries/steps, webhook deliveries; readiness line printed only after first successful tick; boots declaring REAL vs fake email out loud.
invariants: one campaign/job failure doesn't kill the tick; errors logged message-only (pg constraint detail embeds contact PII).
confidence: verified

### adapters — provider implementations behind ports
purpose: fake (zero network), queue-inprocess (Postgres-as-queue), email-resend, ai-gemini, webhook-http.
path_prefixes: packages/adapters
key_files: packages/adapters/fake/src/index.ts, queue-inprocess/src/index.ts, email-resend/src/index.ts, ai-gemini/src/{index,prompt}.ts, webhook-http/src/index.ts
entrypoints: constructed in apps/*/src/container.ts
responsibilities: swap providers via container change only; audit:security gate fails if fake/ imports http clients.
invariants: fakes perform ZERO network I/O; real email requires BOTH key+from (half-configured ⇒ fake, never default-address sending).
pitfalls: queue visibility timeout coarse/fixed; ordering best-effort (ponytail comments name BullMQ upgrade path).
confidence: verified

## FLOWS

### signup-verify-workspace-invite (CUJ-1)
trigger: POST /v1/auth/signup (or web form → /api/signup proxy)
steps: 1. throttle(5/min, ip-keyed) + zod 2. signUp creates user + verification token (scrypt pw) 3. if EmailPort+PUBLIC_WEB_URL configured: send verification email, else echo token only when exposeVerificationToken=true (non-prod/tests) 4. verifyEmail consumes token 5. login sets httpOnly SameSite=Lax cookie (host-only) 6. createWorkspace assigns owner membership + default plan 7. inviteMember (owner/admin only, throttled) emails bound link → /invitation page accepts with session, binding to invitee address.
files: apps/api/src/app.ts, packages/core/src/identity/service.ts, apps/web/src/app/api/login/route.ts, apps/web/src/lib/actions.ts
confidence: verified

### csv-import (CUJ-2)
trigger: upload in /app/contacts/import
steps: 1. base64 file → createImportPreview parses CSV/XLSX (bounded), normalizes, dedupes, persists plan rows 2. UI shows summary + sample + mapping 3. optional remap re-previews 4. commitImport applies plan creating/updating contacts + audit.
files: packages/core/src/imports/{sheet,dryRun,commit}.ts, apps/api/src/app.ts:1082
confidence: verified

### consent-to-send (CUJ-3)
trigger: POST …/consent or suppression, then any send attempt
steps: 1. recordConsent supersedes previous current row (trigger) 2. at execution dispatch calls checkSendAllowed → evaluateSendGate (suppression FIRST, then exact-channel granted required) 3. blocked ⇒ delivery_attempt 'suppressed' + message failed permanently.
files: packages/core/src/consent/{gate,repository}.ts, packages/core/src/delivery/dispatch.ts:136
confidence: verified

### segment-build-and-snapshot (CUJ-4)
trigger: /app/segments builder
steps: 1. AST validated client-side shape → POST segments/preview returns count+sample (compiled parameterised SQL) 2. save dynamic segment 3. campaign audience selects segments 4. approval freezes static snapshot member ids under repeatable read.
files: packages/core/src/segments/{ast,compile}.ts, packages/core/src/campaigns/approval.ts
confidence: verified

### campaign-launch (CUJ-5)
trigger: builder tabs → submit
steps: 1. configure basics/audience/channels/content/tracking 2. blockers computed (missing consent surface, unfrozen content…) 3. submit→in_review 4. approve by non-submitter with segments:write-class rights: audience certified, active version frozen, status scheduled 5. worker tickCampaignStarts flips scheduled→running (engine actor) + materializeMessages inserts one row per recipient×variant 6. worker claims batches (skip locked) → dispatch gates → port.send → status/attempts updated 7. pause/stop per state machine; emergency-stop endpoint halts mid-flight.
files: packages/core/src/campaigns/{state,approval,blockers}.ts, apps/worker/src/main.ts:52, packages/core/src/delivery/dispatch.ts, apps/api/src/deliveryRoutes.ts
confidence: verified

### journey-execution (CUJ-6)
trigger: publish journey
steps: 1. canvas edits draft graph (immutable published version on publish) 2. worker polls entry criteria → enrollDueContacts creates enrollments 3. steps claimed → executeStep advances (wait schedules future, branch evaluates, task creates sales_task, send inserts message row) 4. message flows through the SAME campaign dispatch path.
files: packages/core/src/journeys/{enroll,execute,wait}.ts, apps/worker/src/main.ts:98
confidence: verified

### engagement-attribution (CUJ-7)
trigger: provider webhook or partner POST …/events
steps: 1. Resend Svix-HMAC verify over raw bytes, replay-bounded, idempotent on svix-id → applyProviderDeliveryEvent updates message status; bounce/complaint auto-suppresses 2. partner events ingested via API key 3. conversions attributed last-touch within windowDays of contact's most recent send 4. report/dashboard reconcile; CSV export available; ROI withheld when incomplete.
files: apps/api/src/providerWebhookRoutes.ts, packages/core/src/delivery/providerEventIngest.ts, packages/core/src/analytics/{repository,attribution,roi}.ts
confidence: verified

### outbound-webhook-delivery
trigger: any of 8 domain events with active subscription
steps: 1. emission inserts webhook_deliveries 2. worker claims → signs payload (HMAC, timestamped) 3. WebhookHttpPort posts (urlGuard SSRF checks) 4. non-2xx/timeout retries backoff up to MAX_ATTEMPTS 5. redeliver endpoint forces requeue.
files: packages/core/src/webhooks/{dispatch,signing,urlGuard}.ts, packages/adapters/webhook-http/src/index.ts
confidence: verified

## APIS

~110 routes total (>40): conventions — all under `/v1`; workspace-scoped paths `/v1/workspaces/:workspaceId/...` resolved via `requireMember(permission)` (membership 404s non-members, RBAC via assertCan); zod `parse()` on every body/param/query; partner read surface + `POST .../events` authenticate via Bearer API key (`requireApiKey`, apps/api/src/apiKeyAuth.ts); health at `/healthz`,`/readyz`. Session-auth routes set/read cookie `campify_session`. Representative examples:

| method | route | handler file:symbol | auth | notes |
|---|---|---|---|---|
| POST | /v1/auth/signup | apps/api/src/app.ts:buildApp | none (throttled) | emails verification token; echoes only when exposeVerificationToken |
| POST | /v1/auth/login | apps/api/src/app.ts:buildApp | none (scrypt-throttled first) | sets httpOnly cookie; timing-equalized |
| GET | /v1/me | apps/api/src/app.ts:buildApp | session | session validation target for web middleware |
| POST | /v1/workspaces | apps/api/src/app.ts:buildApp | session | throttled AFTER auth so bucket keys on user |
| PATCH | /v1/workspaces/:wid/members/:userId | apps/api/src/app.ts:buildApp | users:manage | owner-only for owner role; last-owner guard inside UPDATE |
| POST | /v1/workspaces/:wid/invitations | apps/api/src/app.ts:buildApp | users:manage + throttle | returns `{delivered:true}` else token; never both |
| GET | /v1/workspaces/:wid/contacts | apps/api/src/app.ts:buildApp | contacts:read | offset>0 needs data:export (paging = export) |
| POST | /v1/workspaces/:wid/imports/preview | apps/api/src/app.ts:buildApp | imports:run | 20MB bodyLimit + pre-read auth guard |
| POST | /v1/workspaces/:wid/segments/preview | apps/api/src/app.ts:buildApp | segments:read | throttled: compiled queries can be expensive |
| POST | /v1/workspaces/:wid/campaigns/:id/approve | apps/api/src/campaignRoutes.ts:registerCampaignRoutes | campaign:approve | four-eyes; freezes version+audience |
| POST | /v1/workspaces/:wid/campaigns/:id/transition | apps/api/src/campaignRoutes.ts:registerCampaignRoutes | varies | hardened after approve-bypass bug (fac3d6d) |
| POST | /v1/workspaces/:wid/campaigns/:id/ai/suggest | apps/api/src/campaignRoutes.ts:registerCampaignRoutes | ai:use | suggestion only; separate audited /ai/accept |
| POST | /v1/workspaces/:wid/emergency-stops | apps/api/src/deliveryRoutes.ts:registerDeliveryRoutes | campaign:admin-class | scoped workspace/channel/campaign |
| POST | /v1/providers/resend/webhook | apps/api/src/providerWebhookRoutes.ts:registerProviderWebhookRoutes | HMAC (svix) | raw-body verified; secret absent ⇒ all refused |
| POST | /v1/workspaces/:wid/events | apps/api/src/analyticsRoutes.ts:registerAnalyticsRoutes | API key | event ingestion |
| GET | /v1/workspaces/:wid/campaigns/:id/report.csv | apps/api/src/analyticsRoutes.ts:registerAnalyticsRoutes | session | discloses attribution model per §15.3 |
| GET | /v1/workspaces/:wid/conversions | apps/api/src/apiReadRoutes.ts:registerApiReadRoutes | API key | partner read surface |
| POST | /v1/workspaces/:wid/journeys/:id/publish | apps/api/src/journeyRoutes.ts:registerJourneyRoutes | journeys:publish | immutable version created |
| POST | /v1/workspaces/:wid/sales-tasks/:id/transition | apps/api/src/salesTaskRoutes.ts:registerSalesTaskRoutes | sales perms | table-driven legality |
| POST | /v1/workspaces/:wid/crm/deals/:id/outcome | apps/api/src/crmRoutes.ts:registerCrmRoutes | crm perms | won/lost closes deal |
| POST | /v1/workspaces/:wid/webhook-deliveries/:id/redeliver | apps/api/src/webhookRoutes.ts:registerWebhookRoutes | webhooks:manage | forces requeue |

Full inventory greppable via `rg "app\.(get|post|put|patch|delete)" apps/api/src apps/web/src`.

## DATABASE

Engine: PostgreSQL 18.4 (embedded-postgres locally on 5434; managed later [uncertain]). 78 migration files = 39 up/down SQL pairs + one JS pair (0014_suppression_backfill_via_domain.mjs — backfill executed THROUGH the domain layer so normalization/supersede logic stays single-sourced). Runner: scripts/db.mjs; `pnpm db:verify` migrates clean DB then asserts FORCE RLS everywhere, app role not superuser/no BYPASSRLS, down-file presence.

Roles: `postgres` (superuser; init+migrations via DATABASE_MIGRATION_URL) vs `campify_app` (NOBYPASSRLS non-superuser; all serving traffic). Role-level statement/idle timeouts set in migration 0011.

~60 tables. Meaningful groups:
- Identity/global: users, sessions (token_hash), verification_tokens, invitations, memberships (composite PK w/ workspaces), workspaces, audit_log + auth_audit_log (append-only: UPDATE/DELETE revoked + immutability triggers), rate_limit_windows.
- Audience: contacts, contact_fields, tags, contact_tags, lists, list_members, import_jobs/import_rows (persisted dry-run plan), suppressions, consent_records (+consent_supersede() trigger enforcing one current row/channel; unique key carries workspace_id since ADR-0010).
- Segments: segments, segment_versions, segment_members (static snapshots).
- Campaigns: campaigns, campaign_versions (immutable after approval via trigger), campaign_approvals (four-eyes), campaign_audiences/_members/_snapshots (snapshot_write_once trigger), campaign_channels/_exclusions/_tracking_rules/_test_recipients, campaign_comments.
- Content: content_items/_variants/_versions (append-only trigger)/content_templates/content_comments, ai_suggestions (requestFingerprint ties accept↔suggest).
- Delivery: messages (status, next_attempt_at doubles as due-time + claim-expiry; sent_at added 0031 as attribution anchor), delivery_attempts, emergency_stops, send_frequency, provider_delivery_events; SECURITY DEFINER due_messages().
- Journeys: journeys/_versions/_nodes/_edges (graph immutability triggers), journey_enrollments, journey_step_executions; due_journey_entries()/due_journey_steps() SECURITY DEFINER.
- Analytics: events, conversions (attribution_model enum column), api_keys (find_active_api_key() SECURITY DEFINER for pre-scope lookup).
- Sales/CRM: sales_tasks, companies, pipeline_stages (seed_default_pipeline()), deals, crm_activities.
- Plans: plans, workspace_plans (INSERT/UPDATE/DELETE revoked from app role — ceilings unreachable from any route), usage_counters (usage_counters_never_decrease() trigger).
- Webhooks: webhook_subscriptions (plaintext secrets — known debt), webhook_deliveries; due_webhook_deliveries().

No vector stores, no Redis/cache layer. Caching: none beyond config memoization [verified by absence].

RLS: every tenant table `ENABLE`+`FORCE`, policy `tenant_isolation` on `current_setting('app.workspace_id')::uuid`; composite FK rule enforced by schema-derived test (packages/db/test/fk-isolation.tenancy.test.ts); tenancy suite derives table list from live schema and attacks select/delete/re-parent/insert behaviourally (packages/db/test/all-tables.tenancy.test.ts).

## TESTS

Frameworks: vitest 3 workspaces (vitest.workspace.ts projects unit/integration/tenancy/contract/e2e — filename-suffix driven: *.unit / *.integration / *.tenancy / *.contract / *.e2e.test.ts) + Playwright (playwright.config.ts, chromium only, ports 3300/3301, serial, retries=0 deliberately).

Commands: `pnpm test:unit`, `test:integration`, `test:tenancy`, `test:contract`, `test:e2e` (HTTP-level, boots real servers :3100/:3101), `test:browser` (Playwright), and umbrella `pnpm verify` (format→lint→typecheck→unit→db:verify→integration→tenancy→contract→audit:security→build→smoke:boot→e2e→seo).

Layout/mapping heuristics observed:
- Unit tests colocated `.unit.test.ts` next to sources (RBAC matrix, state machines, consent gate, segment compiler hostile-input tests, i18n parity in apps/web).
- Integration tests in packages/core/test/*.integration.test.ts (domain vs real embedded PG with RLS active) and apps/worker/test/*.pipeline.integration.test.ts (full materialize→claim→dispatch — lives in worker because core can't depend on adapters).
- Tenancy ONLY in packages/db/test/*.tenancy.test.ts; derives tables from live schema (new tenant table without coverage FAILS).
- Contract tests in apps/api/test/*.contract.test.ts (status codes, authz matrix, cross-tenant attacks over HTTP, token-leak asserted on serialized body).
- E2E: apps/web/test/smoke.e2e.test.ts drives signup→workspace→import→consent→segment→campaign over HTTP asserting rendered HTML/RTL/noindex; e2e/campaign.spec.ts is the Playwright browser suite (form submission, cookies, redirects).
- Integration suites share one DB and are forced single-fork to serialize (vitest.workspace.ts:33-38).
- Auth throttles constrain test design: suites share/mint accounts carefully (smoke.e2e.test.ts sharedAccount()).

CI (.github/workflows/verify.yml): runs `pnpm verify` itself (no second gate list to drift), embedded PG on 5434, NO provider credentials ever — CI performs zero network I/O, builds TS packages before migrating (migration 0014 imports built core).

## GIT LESSONS

109 commits, linear narrative M1→M18, each citing PRD IDs. Durable lessons:

- **Test what attacks, not what decorates.** Original isolation suite asserted policy metadata on 15/17 tables and attacked 2 — metadata was perfect and a cross-tenant WRITE still existed. Now: behavioural attack on EVERY table, schema-derived. (ADR-0010 lesson; commits 1e7ead5, ea32541)
- **Referential integrity bypasses RLS.** PG runs FK checks with RLS disabled as table owner; single-column FKs let a tenant reference another tenant's rows and CASCADE-delete them. Fix: composite (workspace_id,id) FKs everywhere (migration 0007; ADR-0010).
- **Fail-closed defaults everywhere.** NODE_ENV once defaulted to 'development' → production booted with token echo + non-Secure cookies (578b127; now required, no default, config/index.ts:8). Absent Origin header treated as proof → login CSRF (9e536dd; now positive evidence required, apps/web/src/app/api/login/route.ts:32). Cookie-shape session checks → middleware now VALIDATES via /v1/me failing closed (middleware.ts:53).
- **trustProxy is dangerous in both directions:** `true` made rate-limiting evadable AND a lockout weapon (9f85161); hop-count `1` still evadable — trust by ADDRESS only, default nobody (app.ts:231-243). After the BFF landed, per-IP buckets collapsed entirely (all requests arrive from Next server) → key authenticated throttles on userId (documented at app.ts:566).
- **A takeover came from partial hardening:** making changeRole/removeMember owner-only but not inviteMember left an escalation path (ea32541). Rule: harden ALL sibling paths or none; guards belong INSIDE the statement with `for update`.
- **PII leaks through logs in surprising channels:** pg constraint errors embed offending rows in `detail`/`message`; Fastify request logs include query strings (tokens). Fixes: log structural fields only for driver errors, disableRequestLogging, log route PATTERN not resolved path (96b84db, app.ts:293-305, 538-559).
- **Resource-exhaustion cluster (M1 rounds):** quadratic XLSX parse, unbounded zip inflation, lazy-regex quantifiers, N+1 auth cost, 30×20MB anonymous bodies ≈1GB heap (presence-cookie "guard" bypassed), unbounded segment previews starving other tenants (56s COUNT). Fixes: budgets/caps/batches/timeouts + throttles on expensive-but-legal operations (063c501, fb73083, 40e66ad, 89b8ad2, 1cdde20).
- **The API must not lie about execution:** generic transition route could approve a campaign through the wrong permission (fac3d6d); engine-only transitions unreachable over HTTP by construction (actor defaults 'api', state.ts:220).
- **Traceability honesty:** FIVE traceability rows claimed UI screens "verified" that were never built (A/B settings, consent UI, import wizard, segment builder, members screen) — pattern recorded in PROGRESS.md: *a row whose Verification column names only domain tests cannot support a claim about the product*. Also invented IDs caught (AC-14, FR-AI-001..004 in commit subject 1739f25) and an A-09 assumption cited for months before being registered (ARCHITECTURE_DECISIONS.md:213).
- **Production taught what staging couldn't:** signup shipped 201-with-no-way-to-finish (no email delivery); invitation emails pointed at a /invitation page that didn't exist until M18 (760fbf6); half-configured Resend silently skipped mail (warn added, app.ts:282); PUBLIC_WEB_URL-less links to 127.0.0.1 (a38a0c8).
- **Reverted approach:** ADR-0011 explicitly REVERSES an M1-close recommendation (reduce web tier to static shell, defer designed auth) after analysis showed churn was implementation quality, not architecture; BFF kept. Failed-state-as-terminal was locked in by a test and reversed when rereading PRD §7.2 (state.ts:185). Earlier `scheduled->stopped`/`running->stopped` transitions removed as not in spec.
- **Attribution anchoring:** conversions drifted until anchored on messages.sent_at (cf88b83); queue-suite flake fixed same commit (NFR-REL-002 culture: a flaky gate is a defect).
- **Dangerous areas for future agents:** anything touching tenant scope (withTenant discipline, SECURITY DEFINER allowlist), the consent gate (legal), the RBAC matrix + owner-role paths (history of takeover), rate limiter semantics, migration immutability, and the fake-vs-real credential gates (silent network I/O risk).

## DECISIONS

- ADR-0001 working name `campify` — brand/domain (D1) undecided but scaffolding needed — use as npm scope/DB name/hostnames; high reversibility — docs/engineering/ARCHITECTURE_DECISIONS.md#adr-0001
- ADR-0002 pnpm monorepo Next+Fastify+worker — PRD mandates modular monolith, versioned public API awkward in single Next app — apps/packages layout, boundaries enforced by package graph — #adr-0002
- ADR-0003 Postgres RLS + app scoping — top risk is cross-tenant leakage; irreversible — FORCE RLS on current_setting, NOBYPASSRLS role, set_config form; THREE properties verified experimentally before adoption — #adr-0003 (evidence also packages/db/src/tenant.ts)
- ADR-0004 embedded-postgres — no Docker/root on dev machine; PGlite rejected too weak for concurrency evidence — port 5434 (5433 taken by unrelated project ~/Dev/Nabeek); onlyBuiltDependencies needed — #adr-0004
- ADR-0005 strict opt-in consent all channels — D6 legal decision by product owner — single gate, no bypass, suppression re-checked at execution, import can't fabricate consent — #adr-0005
- ADR-0006 Drizzle over Prisma — RLS-friendly typed access — NOTE: actual code uses raw `pg` + hand-written SQL via TenantClient; Drizzle named in ADR appears not adopted [uncertain — maybe abandoned silently] — #adr-0006
- ADR-0007 own-tables auth, scrypt — D9 residency unresolved, vendor PII export would pre-decide it — opaque server-side sessions, httpOnly cookies — #adr-0007
- ADR-0008 segment conditions as stored AST compiled to parameterised SQL — no-code conditions + live counts — AST is the contract, never persist SQL — #adr-0008
- ADR-0009 public/private split in one Next app with 4-layer anti-indexing — SEO-007 — route groups + edge/middleware headers + robots + automated test — #adr-0009
- ADR-0010 composite foreign keys carry the tenant — raised by adversarial review after real cross-tenant WRITE + permanent consent-blocking DoS — every FK into tenant tables composite on (workspace_id,id) — #adr-0010, migration 0007
- ADR-0011 same-origin BFF web auth — reverses M1 recommendation on analysis; third-party-cookie future kills alternative B — explicit trust-boundary table (Sec-Fetch-Site/Origin positive evidence, fail-closed /v1/me validation, TRUSTED_PROXY by address) — #adr-0011
- ADR-0012 Playwright browser E2E — two M1 defects hid behind HTTP-level testing (form pointing at nonexistent route; fabricated-cookie assertion) — browser suite limited to behaviours needing it — #adr-0012
- ADR-0013 native CRM; external connector becomes later integration — target SMB shouldn't buy a second product; D4 blocked indefinitely; raised openly per CLAUDE.md instead of silent reinterpretation — core/crm built; FR-INT-002/003 kept planned — #adr-0013
- Assumption register A-01..A-09 with revisit triggers (incl. Redis/BullMQ deferred, dev-only tokens until EmailPort) — ARCHITECTURE_DECISIONS.md:192-217

## RISKS & TECH DEBT

- **In-process rate limiter**: correct for ONE api instance; N instances multiply limits by N. Single class swap point: apps/api/src/rateLimit.ts (LAUNCH_READINESS §3).
- **Postgres-as-queue**: single-instance ceiling, best-effort ordering, coarse fixed 5-min visibility timeout, no heartbeats (ponytail comments, packages/adapters/queue-inprocess/src/index.ts:16). Load-testing never done against real concurrency (LAUNCH_READINESS §4.7).
- **executiveDashboard N+1** — one campaignReport per campaign (LAUNCH_READINESS §3; ponytail-flagged).
- **Webhook subscription secrets plaintext** in DB (readable to HMAC; RLS-only protection) — KMS path named, nonexistent.
- **Outbound webhooks retry ANY non-2xx all 5 attempts** — deleted endpoints burn budget (core/src/webhooks/dispatch.ts ponytail comment).
- **Attribution last-touch only**, labelled everywhere; second model requires code understanding the enum column (D8 unresolved).
- **SMS/WhatsApp have NO real provider** (D3); CrmPort fake (connector D4-blocked); BillingPort doesn't exist — revenue limits enforced, charging is not.
- **No OpenAPI spec** (FR-INT-008 unstarted) — integrators read doc comments.
- **No platform-operator console** — plan assignment via `pnpm plan` connecting as DB owner (deliberate, but operationally fragile).
- **No resend-verification-email endpoint** (ponytail-noted at app.ts:697) — a user whose send failed is stuck until manually helped.
- **Backup/restore never proven**; migrations never run against a real (non-embedded) instance (LAUNCH_READINESS §4.2-4.3).
- **NODE_ENV/TRUSTED_PROXY/RESEND_WEBHOOK_SECRET misconfiguration classes** each previously caused a production incident; guards exist but rely on operators reading boot warnings.
- **Traceability-vs-reality gap pattern** — five shipped milestones claimed unbuilt screens "verified"; process fix documented but inherently recurring risk (PROGRESS.md M18).
- **Test-suite coupling to throttles**: signup 5/min shapes how e2e suites share accounts; new suites hitting auth limits will produce misleading failures (PROGRESS.md M18).
- **Single shared integration DB + forced single-fork** keeps tenancy honest but serializes CI time as suites grow (vitest.workspace.ts).

## UNCERTAIN

- ADR-0006 says Drizzle ORM chosen; the actual code (packages/db/src/tenant.ts, repositories throughout) uses raw `pg` parameterised SQL with plain interfaces — whether Drizzle was tried and dropped is undocumented. Treat "raw pg" as reality.
- Production deployment details beyond "campify.ai, 13.235.74.89" (PROGRESS.md M14/M16/M17/M18 notes): host, TLS, process manager, backup setup are not in the repo [inferred AWS region ap-south-1 from IP range — uncertain].
- Whether `docs/product/Campaign_Manager_SaaS_PRD_AR.docx` differs from PRD.md (Arabic PRD not diffed here; English engineering docs were read fully, PRD.md skimmed via citations).
- Exact current launch status: LAUNCH_READINESS §4 checklist items (credential rotation, Resend webhook registration in prod, load test) have no recorded completion evidence.
- apps/web dark/light design-system specifics and DESIGN.md referenced in commits (98f8133) — DESIGN.md file not present in tree at analysis time [may have been renamed/removed].
- Migration 0014 (.mjs) mechanics: confirmed to import built @campify/core output; not line-by-line reviewed.
- Contract-test coverage breadth across all ~110 routes (per-route zod schemas are registered ad hoc, not via Fastify serialization) — spot-checked several files only.
