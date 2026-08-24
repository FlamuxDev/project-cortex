# CORTEX REPORT — Mawid-AI

## META
- project_id: mawid-ai
- root: /home/aboud/Dev/Mawid-AI
- kind: multi-tenant B2B SaaS monorepo (AI WhatsApp booking assistant) + desktop shell
- languages: TypeScript 5.7 (strict, ~360 ts/tsx files), Rust (Tauri shell `apps/desktop/src-tauri/src/lib.rs`), SQL (migrations), CSS/Tailwind v4
- frameworks: Next.js 16 App Router + React 19 (`apps/web`), Vercel AI SDK v6 + @ai-sdk/google (Gemini 2.5 Flash), Drizzle ORM, Turborepo 2.3, Tauri 2 (desktop), Tailwind v4 + shadcn/ui
- package_managers: pnpm@9.15.4 workspaces (`pnpm-workspace.yaml`: apps/*, packages/*; `.npmrc` node-linker=hoisted)
- test_frameworks: Node built-in test runner via `tsx --test` (no Jest/Vitest); Rust side untested in CI
- deployment: Docker standalone image built by GitHub Actions → GHCR (`ghcr.io/flamuxdev/mawid-ai:{latest,<sha>}`); EC2 pulls only (never builds); Caddy TLS; prod compose `docker-compose.prod.yml` (postgres+app+caddy); domain gomawid.com; desktop releases via tag `desktop-v*` → `.github/workflows/desktop-release.yml`
- db: PostgreSQL 16 + pgvector (pgvector/pgvector:pg16)

## OVERVIEW
Mawid AI (Arabic موعد, "appointment") is a multi-tenant B2B SaaS: appointment businesses (clinics, salons, workshops — Gulf region) connect a WhatsApp Business number, and an autonomous Gemini agent answers customers in Arabic/English and *actually performs* bookings through tools (search availability, book, confirm, reschedule, cancel, quote price). Owners manage everything in a Next.js dashboard: services/staff/hours/rules CRUD, an inbox with per-conversation AI on/off toggle, calendar, billing (Stripe, env-gated), and an AI preview sandbox that runs the real agent with `dryRun` tools.

The repo has been through three deliberate re-architectures, all visible in git: (1) a "nuclear" layered rebuild of `lib/` into kernel/domain/application/infrastructure (2026-05-17, `1e6acb1`, module-by-module commits), (2) the pnpm+Turborepo split into 4 packages with a lint-enforced one-way dependency graph `web → ai → backend → core` (2026-06-24, `777af5f`), and (3) client-API phases adding a mobile/desktop API layer, FCM push, S3 uploads, refresh tokens, a Tauri desktop shell, and a test-enforced OpenAPI spec (July 2026). CLAUDE.md is the canonical engineering doc (~52KB) and docs/TEAM-GUIDE.md is the onboarding deep-dive.

Tenancy model: one app instance serves all orgs; an inbound WhatsApp message maps to an org by phone-number match; per-org WhatsApp tokens are AES-GCM encrypted at rest (`organizations.whatsapp_access_token_enc` + `WHATSAPP_TOKEN_ENC_KEY` env); platform flags live in the singleton `platform_settings` row. There is no DB-level RLS [verified: no RLS statements in scripts/docker] — tenant isolation is purely application-layer `organization_id` filtering.

Production is live on a single small EC2 box behind Caddy. The defining operational lesson (encoded in CI and docs) is "the server never builds": `next build` on the box once pinned it SSH-unresponsive, so GH Actions builds the image and deploy scripts only pull + run idempotent SQL migrations. Rollback = repoint `MAWID_IMAGE` to a previous sha tag. Docs drift is a recurring theme: README/TEAM-GUIDE still say "68 tests / nazim_session cookie / AI-agent tests deleted", all three now stale vs code (111 tests live-run 2026-08-24, cookie `mawid_session` at `apps/web/lib/auth/session.ts:7`, agent tests restored in `2d5c473`).

## ARCHITECTURE
- **Dependency graph (lint-enforced via ESLint no-restricted-imports + tsconfig paths):** `apps/web → @mawid/ai → @mawid/backend → @mawid/core`. Orchestrators that drive the agent (`whatsapp-inbound`, `meta-channels`) live in `@mawid/ai` precisely so `backend → ai` is impossible. Evidence: README.md:64-84, docs/TEAM-GUIDE.md §2.
- **@mawid/core** (leaf): `packages/core/src/kernel/` (pure datetime w/ Arabic parsing, timezone Intl formatters, booking-rules merge, scheduling context, catalog) + `packages/core/src/db/` (Drizzle schema 36 tables, postgres client `getDb()`).
- **@mawid/backend**: `domain/booking/` (availability, slot-lock booking engine, pricing), `application/{booking,messaging,whatsapp-onboarding}`, `infrastructure/{platform/settings,repositories/message-repository}`, `whatsapp/` (Cloud API client, credentials AES-GCM, webhook verify, send-state idempotency/token-probe, subscriptions, manual-discovery, connection-ownership), `channels/` (shared Meta webhook parse/verify/org-resolve/readiness), `instagram/client.ts` + `messenger/client.ts` (dormant send transports), `payments/` + `stripe/`.
- **@mawid/ai**: `application/ai-agent/` (agent loop, integrity guard, confidential tool-output sanitizer, context builder, preview sandbox, tools/ = 8 Gemini tools), `application/whatsapp-inbound/handle-inbound.ts` (prod orchestrator), `application/meta-channels/handle-inbound.ts` (IG/Messenger foundation — resolves org, records events, never replies yet), `infrastructure/ai/` (gemini sole model build, transcription, rag/{retrieve,sync} pgvector), `industry/` (preset seeds per business type).
- **apps/web**: `app/api/**` 59 route files (auth, dashboard CRUD, webhooks, cron, mobile, stripe, health); `app/(marketing|dashboard|admin)` pages; `lib/` Next-bound glue: auth/session+refresh, api-client (typed client for desktop/mobile), dashboard read-models (`requireOrganizationApi` at lib/dashboard/org.ts:62), i18n ar/en dictionaries, billing, push (FCM firebase-admin), uploads (S3 presigner), email (Resend), cron auth, rate-limit, error-tracking (Sentry), desktop bridge + releases.
- **apps/desktop**: Tauri 2 hosted-URL shell of gomawid.com; tray, notifications, unread badge polling, global shortcuts, autostart, prefs JSON; `mawid://` deep links mapped back into web URLs (`src-tauri/src/lib.rs` `deep_link_to_web_url`). Uncommitted WIP: `scripts/tauri-prereq-checker.mjs` (+ its .test.mjs, not wired into turbo).
- **Entrypoints**: HTTP routes are the only programmatic entrypoints; long-running work is cron-over-HTTP (`/api/cron/*`) triggered by server crontab (`scripts/setup-server-cron.sh`). No queues/workers — debounce/idempotency done inline.
- **Jobs**: reminders (24h/2h offsets, atomic JSONB claim), no-show sweep, recurring-series expansion.
- **Integrations**: Meta WhatsApp Cloud API (Graph v20), Gemini + gemini-embedding-001 (768-dim), Stripe (deposits + subscriptions, env-gated), Firebase Cloud Messaging, AWS S3 presigned uploads, Resend email, Sentry.
- **Deploy pipeline**: push main → `.github/workflows/deploy.yml` builds/pushes image → `scripts/deploy-to-ec2.sh` rsyncs config (excludes secrets) → `scripts/server-up.sh` runs migrations ORDER list + compose pull/up. Caddyfile is a single-file bind mount needing `--force-recreate caddy` after edits (inode gotcha).

## MODULES

### core-kernel — Pure shared kernel
purpose: deterministic date/timezone/booking-rule logic; zero intra-repo imports (true leaf).
path_prefixes: packages/core/src/kernel/
key_files: datetime.ts (Arabic date parse, `afternoonWallClockGuess` 02:30→14:30), timezone.ts (`formatSlotLabel` — must use discrete Intl options, never weekday+dateStyle mix which throws), booking-rules.ts (`BookingRules`/`mergeBookingRules`/`effectiveBookingRules`), scheduling.ts (`buildSchedulingContext` calendar block for prompts), catalog.ts
entrypoints: library only
responsibilities: wall-clock↔UTC conversion, slot label formatting, rule merging, prompt calendar
invariants: no imports outside kernel; all date math flows through here, never ad-hoc `new Date()` arithmetic in callers
pitfalls: Intl option mixing throws; Arabic-Indic digits need `tabular-nums` (Plex Mono can't render them)
confidence: high

### core-db — Schema + client SSOT
purpose: Drizzle schema (36 tables) + pooled postgres client.
path_prefixes: packages/core/src/db/
key_files: schema.ts, index.ts (DbClient/DbOrTx)
entrypoints: drizzle.config.ts points here (`pnpm db:*`)
responsibilities: table definitions, types ($inferSelect), transaction handle type
invariants: any column added here must also get an idempotent SQL file in scripts/ + ORDER entry in server-up.sh
pitfalls: dev uses `db:push`; prod uses hand-written SQL — schema.ts alone does NOT migrate prod
confidence: high

### backend-domain-booking — Booking engine
purpose: pure-ish business rules for availability and slot-safe writes.
path_prefixes: packages/backend/src/domain/booking/
key_files: rules.ts (`canBookSlot`, cancel/reschedule windows, party size), availability.ts (`getAvailableSlots`, `intervalsOverlap` single source of truth, work-hours), book.ts (`validateAndBookSlot` :296, `applyRescheduleWithSlotLock` :499 owns price-on-reschedule recompute, `acquireSlotBookingLock` :625 = `pg_advisory_xact_lock(hashtext(scope))` inside txn, RRULE `expandRecurringOccurrences` :664, operator-only `skipSlotCheck`), pricing.ts (staff→time_band→vip→flat fallback then offers)
entrypoints: called from application layer + AI tools + dashboard APIs
responsibilities: enforce notice hours, same-day, max advance, party size, staff/resource/group-seat collision
invariants: imports kernel + db only (no ai/messaging/infra/app); paymentsEnabled flag injected by caller — domain does no settings I/O; NO "one active booking per customer/service" rule exists (documented non-feature)
pitfalls: slot lock scope must include the collision dimension or double-booking returns; staff must be linked via staff_services (`ensureDefaultStaffServiceLinks` :635) else `slot_unavailable`
confidence: high

### backend-whatsapp — Cloud API infrastructure
purpose: all Graph API I/O + credential crypto + webhook verification.
path_prefixes: packages/backend/src/whatsapp/
key_files: client.ts (send + typing indicator/renewal), credentials.ts (AES-GCM decrypt, `plain:` fallback when WHATSAPP_TOKEN_ENC_KEY unset), webhook.ts (`verifyMetaWebhookSignature`, `resolveOrganizationFromWebhook` display#↔org), send-state.ts (outbound idempotency via inbound wamid, token probe cache, last_error flags), graph.ts, subscriptions.ts (`subscribeAppToWaba` — routes tenant WABA to our single app webhook), manual-discovery.ts, connection-ownership.ts, index.ts barrel
entrypoints: library
responsibilities: signature verification, send, typing, token lifecycle, subscription repair
invariants: per-org encrypted tokens only; no shared production WHATSAPP_ACCESS_TOKEN; no QR/Baileys path ever (ToS ban risk — explicit owner directive)
pitfalls: stored `whatsapp_status=verified` reflects save-time state — tokens expire later; probe cache must be cleared on reconnect
confidence: high

### backend-messaging — Lifecycle/reminders/outbound
purpose: post-booking confirmations, cron reminders, template rendering, deposit gating.
path_prefixes: packages/backend/src/application/messaging/, application/booking/book-appointment.ts
key_files: reminders.ts (`runAppointmentReminders`, offsets default [24,2]h ±45min window, atomic claim on appointments.reminders_sent JSONB `__pending__`→ISO ts, released on failure), lifecycle.ts (confirmation skip for pending_deposit/cancelled; re-exports deposit.ts intentionally), outbound.ts (org templates ▸ bilingual fallback render), templates.ts, deposit.ts (owns schema access), ../booking/book-appointment.ts (`bookAppointment` use-case fires notifyAppointmentBooked)
invariants: parallel cron runs cannot double-send (atomic claim); confirmation sent once per appointment
pitfalls: broken-import regression guard exists as deposit.test.ts
confidence: high

### backend-channels-meta — Multichannel foundation (dormant)
purpose: shared Meta webhook plumbing for Messenger/Instagram alongside WhatsApp.
path_prefixes: packages/backend/src/channels/, instagram/, messenger/
key_files: meta-webhook.ts (+test), resolve-org.ts (page_id/instagram_account_id lookup), webhook-verify.ts, readiness.ts (public diagnostics), messenger/client.ts + instagram/client.ts (env-gated, currently not configured)
invariants: meta-channels orchestrator never replies before per-tenant page tokens + App Review land (see ai-meta-channels below); org routing columns exist but no token columns yet (scripts/018_meta_channels.sql)
confidence: high

### backend-infra — Settings + message repository
purpose: platform flag resolution and the centralized history-read invariant.
path_prefixes: packages/backend/src/infrastructure/
key_files: platform/settings.ts (`isPaymentsEnabled`, `getPlatformCronSecret`), repositories/message-repository.ts (loads RECENT history in correct order — the prod-outage invariant from bef6b1d lives here)
invariants: never read conversation history raw/oldest-first anywhere else
confidence: high

### backend-payments-stripe — Deposits & webhooks
purpose: optional deposit checkout + webhook verification.
path_prefixes: packages/backend/src/payments/, stripe/
key_files: payments/stripe-appointment-deposit.ts, stripe/verify-webhook.ts; consumer route apps/web/app/api/stripe/webhook/route.ts (checkout.session.completed → appointment status pending_deposit→scheduled :27,:46)
invariants: inert until STRIPE_SECRET_KEY set AND platform_settings.payments_enabled=true; only verified events processed
confidence: high

### ai-agent — The Gemini agent
purpose: system prompt + tool-calling loop + the single server integrity invariant.
path_prefixes: packages/ai/src/application/ai-agent/
key_files: agent.ts (`buildMessages` 6-rule history normalization — final turn always user; `runWhatsAppAgent` generateText toolChoice auto stopWhen stepCountIs(8); integrity retry once with INTEGRITY_NUDGE then drop text; `fallbackReply`), guard.ts (`collectToolOutcomes`/`checkIntegrity` AR+EN claim regexes — see §B.1 in CLAUDE.md, the SOLE written spec), confidential.ts (`sanitizeToolOutput` strips secret-shaped keys/values, fail-open on shape, never strips appointment_id/scheduled_at), context.ts (`loadAgentContext`: history+services+RAG+profile+scheduling), preview.ts (`runAgentPreview`, dryRun:true tools :144), tools/ (names.ts AGENT_TOOL_NAMES: get_business_snapshot, list_customer_appointments, search_availability, book_appointment, confirm_appointment, cancel_appointment, reschedule_appointment, quote_price)
entrypoints: whatsapp-inbound orchestrator; /api/dashboard/ai/preview
invariants: §B.1 contract — never feed raw ctx.history to generateText; thinking disabled (`AGENT_MODEL_SETTINGS` temperature 0, maxOutputTokens 2048, thinkingBudget 0 in infrastructure/ai/gemini.ts); model decides every tool call (no keyword routing, no reply re-authoring — deleted regex layers must not return)
pitfalls: two independent causes of "Gemini 200 + empty candidates": malformed history AND thinking eating token budget; both caused the same prod outage once
confidence: high

### ai-inbound-orchestrators — whatsapp-inbound & meta-channels
purpose: drive the agent from channel events; keep backend free of ai imports.
path_prefixes: packages/ai/src/application/whatsapp-inbound/, meta-channels/
key_files: whatsapp-inbound/handle-inbound.ts (`generateAndSendAiReplyForInbound`: ai_handled gate :84, wamid idempotency :89/:131, 1800ms debounce :28/:94, token probe :107, typing renewal, send + persist outbound + usage_stats), index.ts; meta-channels/handle-inbound.ts (`handleMetaChannelInbound` — resolve→record only, typed outcomes, TODO plug point for AI reply)
invariants: pure orchestration; send-state plumbing lives in backend/whatsapp/send-state.ts
confidence: high

### ai-infrastructure — Model, transcription, RAG
purpose: sole Gemini build site; voice transcription; org knowledge embeddings.
path_prefixes: packages/ai/src/infrastructure/ai/
key_files: gemini.ts (AGENT_MODEL_SETTINGS — the only place model settings may change), transcription.ts, rag/retrieve.ts + sync.ts (organization_knowledge_chunks, 768-dim vector search)
invariants: build the model nowhere else; do not re-enable thinking without raising maxOutputTokens far above reasoning ceiling
confidence: high

### ai-industry — Industry presets
purpose: seed services/catalog per business vertical chosen at signup.
path_prefixes: packages/ai/src/industry/
key_files: seed-catalog.ts, seed-industry-preset.ts, appointment-presets.ts
notes: industry is collected once at signup (`/api/auth/register` seeds it), editable in Settings; deliberately NOT a setup-wizard step (deleted step, do not reintroduce)
confidence: high

### web-app — Next.js surfaces
purpose: marketing site, auth pages, owner dashboard, admin, all API routes.
path_prefixes: apps/web/app/
key_files: app/api/** (59 route.ts), dashboard/{overview,business,calendar,settings,setup,account,billing,ops}, admin/{leads,organizations}, public/openapi.json + api-docs.html (/api-docs redirect, next.config.mjs redirects block)
invariants: setup wizard fully optional/non-gated (no SetupGuard — deleted); dashboard auth via `requireOrganizationApi` (apps/web/lib/dashboard/org.ts:62); i18n via dictionaries, no [locale] URL segments
confidence: high

### web-lib-client-api — Client API layer (desktop/mobile parity)
purpose: single typed client + bearer/refresh auth for desktop & Flutter clients.
path_prefixes: apps/web/lib/api-client/, mobile/, account/, email/, push/, uploads/, desktop/
key_files: api-client/{config,fetch,auth,endpoints/{dashboard,auth}} (+3 test files), mobile/stripe-return-urls.ts (allow-list), push/firebase.ts + send.ts (FCM fan-out on inbound messages), uploads/presign.ts (S3, 5MB default cap, purpose-scoped keys), email/send.ts (Resend; reset URL allow-listed against stripe-return host list), desktop/{desktop-chrome,native-bridge}.ts, desktop-releases.ts (/download page feed)
confidence: medium-high (breadth verified; deep behavior not traced line-by-line)

### desktop-shell — Tauri wrapper
purpose: native window over hosted web app; deep links return OAuth/billing flows to web destinations.
path_prefixes: apps/desktop/
key_files: src-tauri/src/lib.rs (deep_link_to_web_url, tray, shortcuts, autostart, DesktopPreferences JSON persistence), src-tauri/tauri.conf.json, shell/index.html (loading placeholder)
invariants: v1 is hosted-URL shell — no local backend; release builds hardcode PRODUCTION_APP_URL
confidence: high

### openapi-spec — Contract & Swagger UI
purpose: machine-checked API documentation without codegen dependency.
path_prefixes: apps/web/public/, docs/
key_files: public/openapi.json (1428 lines, all 59 routes), public/api-docs.html (CDN-loaded Swagger UI), lib/openapi.test.ts (walks app/api/**/route.ts; fails if route+method missing OR spec documents nonexistent route), docs/mobile-api.openapi.yaml (hand-written YAML twin — STALE, still lists deleted endpoints)
confidence: high

## FLOWS

### WhatsApp inbound → AI reply (the critical path)
trigger: Meta POST /api/whatsapp/webhook (text or audio)
steps: verify x-hub-signature-256 (WHATSAPP_APP_SECRET→FACEBOOK_APP_SECRET→META_APP_SECRET fallback) → resolve org (display number ↔ graph phone_number_id) → dedupe by whatsapp_message_id unique index (23505 tolerated) → upsert customer/conversation (open, ai_handled=true) → persist inbound + bump unread → FCM notify owner → if ai_handled: `generateAndSendAiReplyForInbound` (idempotency check on inbound wamid → 1.8s debounce → loadAgentContext → paymentsEnabled injection → credential resolve → token probe (forced if last_error) → typing indicator + renewal → createAgentTools(dryRun off) → runWhatsAppAgent → integrity guard → send → persist outbound + clear error + usage_stats)
files: apps/web/app/api/whatsapp/webhook/route.ts; packages/backend/src/whatsapp/{webhook,client,credentials,send-state}.ts; packages/ai/src/application/whatsapp-inbound/handle-inbound.ts; packages/ai/src/application/ai-agent/{agent,guard,context}.ts
confidence: high (read end-to-end)

### AI-driven booking
trigger: customer asks to book inside WhatsApp thread
steps: agent calls search_availability → presents options → requires explicit customer yes naming service+time → book_appointment → domain `validateAndBookSlot` under `pg_advisory_xact_lock` → application `bookAppointment` sends confirmation message via messaging/lifecycle → guard grounds the reply in tool output
files: packages/ai/src/application/ai-agent/tools/{slot-query,appointments}.ts; packages/backend/src/domain/booking/book.ts; packages/backend/src/application/booking/book-appointment.ts
confidence: high

### Deposit payment
trigger: booking rule requires deposit OR dashboard action
steps: validateAndBookSlot sets status pending_deposit (paymentsEnabled injected) → /api/dashboard/appointments/[id]/deposit-checkout creates Stripe session → customer pays → POST /api/stripe/webhook (signature verified) → checkout.session.completed flips status→scheduled
files: packages/backend/src/payments/stripe-appointment-deposit.ts; apps/web/app/api/stripe/webhook/route.ts:27-46
confidence: high

### Reminder cron
trigger: external cron hits GET /api/cron/appointment-reminders (Bearer/x-cron-secret/platform_settings.cron_secret; 503 unconfigured, 401 mismatch; Vercel x-vercel-cron honored)
steps: find upcoming appointments in offset windows → atomic JSONB claim on reminders_sent → render template bilingual → send per-org decrypted token → record ISO ts per offset
files: apps/web/app/api/cron/*/route.ts; apps/web/lib/cron/verify-cron-request.ts; packages/backend/src/application/messaging/reminders.ts
confidence: high

### Auth (web + client apps)
trigger: login/register or client-app bootstrap
steps: bcrypt password → users row; sessions carry token + refresh_token + expiry pair → web uses mawid_session cookie (middleware proxy.ts updateSession); desktop/mobile use Authorization Bearer + POST /api/auth/refresh rotation; password reset via hashed tokens + Resend email (allow-listed base URL)
files: apps/web/lib/auth/session.ts (:7 SESSION_COOKIE="mawid_session"; refreshSession :96), lib/auth/proxy.ts, lib/email/send.ts
confidence: high

### Deploy
trigger: push to main
steps: GH Actions builds standalone image (NEXT_PUBLIC_APP_URL=https://gomawid.com build-arg, gha cache) → pushes {latest,sha} → operator runs scripts/deploy-to-ec2.sh → rsync (secrets excluded) → server-up.sh: run migrations ORDER → ghcr login via ~/.ghcr-token PAT → compose pull app && up -d → curl /api/health
files: .github/workflows/deploy.yml; scripts/{deploy-to-ec2,server-up,run-migrations}.sh; docker-compose.prod.yml
confidence: high

### Desktop deep-link return
trigger: OAuth/billing completes in system browser → mawid:// scheme
steps: Tauri deep-link plugin → deep_link_to_web_url maps to web URLs (settings?tab=whatsapp, billing success/cancelled, deposit success/cancelled) → WebView navigates
files: apps/desktop/src-tauri/src/lib.rs; apps/desktop/README.md table
confidence: medium-high

## APIS
59 route files under apps/web/app/api. Core conventions: handlers export GET/POST/PUT/PATCH/DELETE from route.ts; dashboard routes begin with `requireOrganizationApi(req)` returning db+org ctx; errors as NextResponse.json; log prefix `[v0]`.

| method | route | handler file:symbol | auth | notes |
|---|---|---|---|---|
| GET | /api/health | app/api/health/route.ts:GET | public | app+database checks |
| POST | /api/whatsapp/webhook | app/api/whatsapp/webhook/route.ts:POST | Meta signature | org resolved by number; full AI pipeline inline |
| GET | /api/whatsapp/webhook | same file:GET | verify token (env or per-org row) | hub challenge |
| GET/PUT/DELETE | /api/mobile/push-token | app/api/mobile/push-token/route.ts | bearer | FCM device registry |
| GET | /api/mobile/bootstrap | app/api/mobile/bootstrap/route.ts | public | plans/locales/presets/support email |
| GET | /api/mobile/whatsapp/status | .../mobile/whatsapp/status/route.ts | bearer | returns connect_options:["manual"] since 303531b |
| POST | /api/mobile/uploads/presign | .../mobile/uploads/presign/route.ts | bearer | S3 presigned PUT |
| POST | /api/mobile/push-test | .../push-test/route.ts | bearer | |
| POST | /api/auth/login · register · logout · refresh · change-password · forgot-password · reset-password | app/api/auth/*/route.ts | public/bearer | refresh rotates sessions rows |
| GET | /api/auth/me | app/api/auth/me/route.ts | session/bearer | session context |
| DELETE | /api/account/delete | app/api/account/delete/route.ts | session | GDPR-style self-delete |
| GET/POST | /api/dashboard/services · staff · resources · templates | app/api/dashboard/<entity>/route.ts | requireOrganizationApi | CRUD families; templates also /[id] |
| GET/POST | /api/dashboard/appointments | .../appointments/route.ts | requireOrganizationApi | calendar data |
| POST | /api/dashboard/appointments/[id]/cancel · deposit-checkout | .../appointments/[id]/*/route.ts | requireOrganizationApi | |
| GET/POST/PATCH | /api/dashboard/conversations(+[id],/read,/retry-ai) | .../conversations/** | requireOrganizationApi | retry-ai re-runs agent |
| GET/PUT | /api/dashboard/organization · scheduling · org-hour-overrides · industry-preset · setup-status · overview | app/api/dashboard/*/route.ts | requireOrganizationApi | read-models/config |
| POST | /api/dashboard/seed-demo | .../seed-demo/route.ts | requireOrganizationApi | demo data seeding |
| GET/POST | /api/dashboard/customers(+[id]/details) | .../customers/** | requireOrganizationApi | |
| GET/POST | /api/dashboard/whatsapp/save-credentials · test-connection · discover · repair · ensure-verify-token · send-test · diagnostics · retry-last | app/api/dashboard/whatsapp/*/route.ts | requireOrganizationApi | manual Cloud-API connect toolkit |
| GET | /api/dashboard/meta/diagnostics | .../meta/diagnostics/route.ts | requireOrganizationApi | readiness report |
| POST | /api/dashboard/ai/preview | .../ai/preview/route.ts | requireOrganizationApi | sandbox, tools dryRun:true |
| GET/POST/DELETE | /api/dashboard/billing(+checkout,portal) | .../billing/** | requireOrganizationApi | Stripe subscriptions, env-gated |
| POST | /api/stripe/webhook | app/api/stripe/webhook/route.ts:POST | Stripe signature | deposit→scheduled |
| GET | /api/cron/appointment-reminders · appointment-no-show · recurring-appointments | app/api/cron/*/route.ts | cron secret | see FLOWS |
| POST | /api/leads | app/api/leads/route.ts | rate-limited public | landing funnel → admin/leads |
| GET/POST | /api/instagram/webhook · /api/messenger/webhook | app/api/{instagram,messenger}/webhook/route.ts | Meta verify/signature | dormant foundation |
| GET/PUT/DELETE | /api/dashboard/templates(+[id]) | .../templates/** | requireOrganizationApi | message templates |

Stale-doc note: docs/mobile-api.openapi.yaml still documents `/api/dashboard/whatsapp/embedded-signup`, `/oauth-url`, `/auth/meta/callback` — all deleted in 303531b. Authoritative spec is public/openapi.json (test-enforced).

## DATABASE
- engines: PostgreSQL 16 + pgvector; Drizzle ORM; schema SSOT packages/core/src/db/schema.ts (36 tables)
- migrations: dev = `drizzle-kit push` (drizzle.config.ts, local :55432); prod = idempotent hand-written SQL scripts/008…018 applied every deploy by scripts/server-up.sh ORDER list; first-boot bootstrap docker/postgres-init.sql (pgcrypto+vector extensions, core tables). Note numbering gap (no 010). 13 sql files total incl. 2 ops resets (clear-conversations.sql, clear-bookings-and-conversations.sql).
- entities (meaning): users/sessions/password_reset_tokens/user_push_devices (accounts; sessions carry access+refresh tokens); organizations (tenant root: plan, industry_preset, booking_rules JSONB, timezone, default_locale, assistant role labels, encrypted WhatsApp token + phone_number_id + verify_token + status/error, unique whatsapp_number/messenger_page_id/instagram_account_id routing ids); platform_settings (singleton 'default': payments_enabled=false, cron_secret); admin_users (staff console for /admin); branches; customers (per-org unique phone, VIP flag, language, tags); conversations (channel, ai_handled toggle, unread_count); messages (direction/sender, unique partial index on whatsapp_message_id — the inbound dedupe); services (bilingual names, duration, buffer/prep, group-booking capacity, pricing_rules JSONB); staff (work_hours JSONB, branch, max_daily_bookings); resources + service_resource_requirements (equipment collision dims); staff_services (M:N capability links); appointments (status machine scheduled/confirmed/pending_deposit/cancelled/no-show?, reminders_sent JSONB per-offset claim map, price, recurring_series_id); recurring_series (RRULE source); appointment_attendees (group seats); appointment_resources; staff_time_off/resource_time_off; org_hour_overrides (per-date closures); appointment_payments (Stripe deposit rows); templates (org message templates); packages/customer_packages (credit packs — dormant); work_orders/work_order_items/field_visits/technician_locations/assets/rentals (field-service vertical — dormant roadmap tables, deliberately kept); appointment_ratings; leads (landing-page funnel with deposit tracking); usage_stats (daily per-org counters: messages, ai_responses, avg_reply_seconds); organization_knowledge_chunks (pgvector 768-dim RAG store, unique org+source+chunk_index).
- RLS: none. Tenant isolation is application-layer org_id filters everywhere [verified absence].
- caches: none at app level except in-process token-probe cache (backend/whatsapp/send-state.ts); turbo build cache only.
- invariant: reminders_sent JSONB doubles as a distributed lock for cron idempotency; messages.whatsapp_message_id unique partial index is webhook dedupe.

## TESTS
- framework: Node:test + assert/strict executed by tsx --test; per-package script `tsx --test $(find src|lib -name '*.test.ts' | sort)`; orchestrated by turbo (`pnpm test`).
- commands: `pnpm test` (all); `pnpm --filter @mawid/core test`; single file `pnpm --filter @mawid/core exec tsx --test src/kernel/datetime.test.ts`; name filter `--test-name-pattern=...`. Gate: tsc --noEmit 0 across 4 workspaces (`pnpm typecheck`) + next build green.
- layout: tests co-located beside source. Verified live 2026-08-24: core 9 cases (datetime, timezone), backend 31 (booking rules/overlap, deposit, reminders, whatsapp webhook, channels meta-webhook), ai 28 (agent, guard, confidential, agent-tools), web 43 (session, client-auth-contract, api-client×3, overview view-models, apply-industry-preset, seed-demo-data, email.send, push.firebase, uploads.presign, stripe-return-urls, openapi parity) = **111 cases / 25 files**, all passing. Desktop has tauri-prereq-checker.test.mjs but its turbo test script is a stub exit-0 (uncommitted WIP).
- mapping highlights: deposit.test.ts guards a historical broken-import regression; agent/guard/confidential tests pin the §B.1 outage fix (deleted once in c542f66 at owner instruction, restored 2d5c473); openapi.test.ts enforces spec↔route parity both directions.
- doc drift warning: README.md:156 and TEAM-GUIDE say "12 files / 68 cases" — stale.

## GIT LESSONS
- `bef6b1d` — "Fix production booking failure: load RECENT history, not the oldest 20": reading history wrong-order/wrong-window silently corrupts agent context. Invariant now centralized in packages/backend/src/infrastructure/repositories/message-repository.ts; never read history elsewhere.
- §B.1 outage lineage — Gemini returned 200 with EMPTY candidates from malformed history (consecutive same-role, trailing assistant) and/or thinking budget consuming maxOutputTokens. Fix = buildMessages normalization + guard.ts + pinned settings (3543d74). Tests were deleted (`c542f66`, owner instruction) leaving the fix unguarded until restored (`2d5c473`): deleting regression tests for live outage fixes is how outages recur.
- `1e6acb1` (+ modules ed6bdee…edfb7b7, merged `a66ac3f`) — big rewrites are safest as ordered, individually-green module commits with a written migration plan; three import cycles (ai⇄booking etc.) were made structurally impossible, not just discouraged.
- `777af5f` — monorepo split landed with a recorded baseline ("tsc 0 · 68 tests · build green") as the acceptance gate; docs/MONOREPO-MIGRATION-PLAN.md kept as the record.
- `d86a1cb` — after `next build` on the EC2 box pinned it SSH-unresponsive: CI builds image, server only pulls. Never build on the box.
- `d4c3895` — adding the Tauri workspace broke the Docker image build (turbo built desktop too); fix scopes the image build to @mawid/web. New workspaces can silently break container builds.
- `d7c10d1` — old domain went NXDOMAIN while new domain already pointed at the box: site was down on every domain until a 14-file domain switch. Domain DNS is a production dependency of the app.
- Caddyfile bind-mount inode gotcha (documented CLAUDE.md/TEAM-GUIDE, no single sha): rsync atomic rename → running container keeps OLD config; plain reload reads stale inode; must `up -d --force-recreate caddy`.
- `303531b` — feature deletion discipline: Embedded Signup removed across component/routes/package/env/flags in one commit with explicit "do not reintroduce" notes + mobile contract change (connect_options:["manual"]); breaking client contract changes are documented in docs/MOBILE-WHATSAPP-FLUTTER.md.
- `1019517` — cheap contract enforcement: a test that walks route.ts files and diffs against openapi.json keeps docs honest without codegen.
- Reverts: none in history; rollback practice is image-tag pinning (`MAWID_IMAGE=<sha>`), with pre-deploy shas recorded in CLAUDE.md per deploy. Dangerous areas: agent.ts/guard.ts (§B.1), message-repository ordering, Caddyfile deploys, anything touching organizations unique columns (23505 crash-loop risk documented in troubleshooting).
- Branch archaeology: feat/production-readiness, redesign/warm-ledger-ui, roy/meta-multichannel-integration, refactor/monorepo-split all merged to main; stale local branches linger. Working tree currently dirty: modified apps/desktop/package.json (prereq-checker scripts) + untracked apps/desktop/scripts/.

## DECISIONS
- One-way package graph web→ai→backend→core — AI tools call the booking domain, so agent-driving orchestrators were placed IN @mawid/ai making backend→ai impossible; enforced by ESLint no-restricted-imports + tsconfig paths — evidence: README.md:59-84, TEAM-GUIDE §2, packages/*/package.json deps.
- Plain agent loop, no intent regexes — five regex routing/synthesis layers were deleted; model decides tools; the ONLY server check is guard.ts integrity — evidence: CLAUDE.md "Removed/do not reintroduce", agent.ts header comments.
- Per-org encrypted tokens over shared token — tenants onboard asynchronously; compromise blast-radius contained; AES-GCM with WHATSAPP_TOKEN_ENC_KEY, `plain:` dev fallback — evidence: packages/backend/src/whatsapp/credentials.ts, schema comment schema.ts:97.
- Manual Cloud-API connect as the only WhatsApp path — Embedded Signup deleted (owner request), QR/Baileys banned (ToS); save/repair call subscribeAppToWaba so Meta routes WABA→our app webhook — evidence: 303531b, packages/backend/src/whatsapp/subscriptions.ts.
- Server never builds — EC2 too small for next build; CI+GHCR pull-only deploy with sha-tagged images for instant rollback — evidence: d86a1cb, .github/workflows/deploy.yml, docker-compose.prod.yml:33-37.
- Hand-written idempotent SQL migrations for prod — drizzle-kit push reserved for dev; avoids destructive auto-migrations against live data; ORDER list in server-up.sh — evidence: scripts/*.sql headers, TEAM-GUIDE §8.
- Payments opt-in at two gates — STRIPE_SECRET_KEY env AND platform_settings.payments_enabled, flag injected INTO the domain rather than domain doing settings I/O — evidence: packages/backend/src/infrastructure/platform/settings.ts, handle-inbound.ts:99, book.ts.
- Test-enforced OpenAPI without codegen — static public/openapi.json + parity test + CDN Swagger UI page — evidence: commit 1019517, apps/web/lib/openapi.test.ts.
- Hosted-URL desktop shell (v1) — zero local backend, same cookies/CORS as browser tab; secure token storage deferred to hypothetical v2 — evidence: apps/desktop/README.md "Architecture".
- Cron-as-endpoint with DB-held secret — platform_settings.cron_secret + header auth + 503-if-unconfigured fail-closed posture — evidence: apps/web/lib/cron/verify-cron-request.ts.

## RISKS & TECH DEBT
- Two OpenAPI specs drifting: docs/mobile-api.openapi.yaml documents 3 deleted endpoints (embedded-signup yaml:933, oauth-url:964, auth/meta/callback:1032); authoritative public/openapi.json is test-pinned. Consolidate or delete the YAML.
- Doc rot cluster: README/TEAM-GUIDE claim 68 tests (actual 111), TEAM-GUIDE says cookie nazim_session (code: mawid_session, session.ts:7), CLAUDE.md ⚠️ says AI-agent tests deleted (they exist). Future agents trusting docs over code will misfire.
- No DB tenancy enforcement: no RLS; one missed `eq(organization_id,…)` in any query = cross-tenant leak [inferred from schema/scripts; consistent with all read paths seen].
- Webhook route does heavy synchronous work (audio download + transcription await) inside POST before returning — risk of Meta webhook timeouts/redeliveries under load; dedupe index mitigates duplicates but latency remains (apps/web/app/api/whatsapp/webhook/route.ts:117-177).
- Uncommitted working-tree state in apps/desktop (package.json + prereq checker + test) — desktop turbo test is a stub; its real .mjs test isn't wired in.
- Dormant-but-present surface area: 7 vertical-expansion tables, instagram/messenger clients, meta-channels orchestrator — kept deliberately, but they widen review surface and invite accidental activation before App Review/per-tenant tokens exist.
- organizations.feature_flags column unused (zero readers); drop deferred (destructive prod migration) — CLAUDE.md.
- Single-box production: postgres+app+caddy on one EC2 host; backup/restore procedure undocumented in repo [uncertain]; no staging environment — deploys go straight to prod after local gates.
- No "one active booking per customer per service" rule — documented product gap, exploitable for spam bookings unless rules added (CLAUDE.md booking section).
- ignoreBuildErrors was removed from next.config.mjs (good) but history shows builds shipped with known TS errors for months; keep tsc gate at 0.
- Rate limiting exists (lib/rate-limit.ts, f5a88d5) but coverage per-route not audited in this pass [uncertain].

## UNCERTAIN
- Whether Meta console was ever fully re-pointed to gomawid.com (webhook callback + domains) — owner-side action marked 🔴 open in CLAUDE.md as of 2026-07-22; WhatsApp inbound may still be undeliverable in prod [cannot verify from repo].
- Whether scripts/017_cleanup_whatsapp_legacy.sql actually ran on production (listed as an open checkbox).
- Current prod runtime version/image sha as of report date (last commit 2026-07-30; no deploy record after 2026-07-22 in docs).
- Exact appointment status vocabulary (e.g., no-show value string) — inferred from cron route names, not exhaustively enumerated.
- Backups/monitoring for prod Postgres — nothing in repo; existence unknown.
- Whether the Flutter mobile client referenced by docs/MOBILE-WHATSAPP-FLUTTER.md and MOBILE-PUSH-FLUTTER.md lives in another repo (not present here) and whether it migrated off the deleted OAuth flow.
- Scope of rate-limit coverage on public endpoints (file exists; per-route application not audited).
- apps/web/lib/account, hooks/, components/ breadth reviewed only by listing, not line-by-line.
