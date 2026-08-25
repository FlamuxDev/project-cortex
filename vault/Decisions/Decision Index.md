---
cortex-generated: true
title: decisions
tags: [decisions]
---
# Decision Index


## [[campify]]
- ADR-0001 working name `campify` — brand/domain (D1) undecided but scaffolding needed — use as npm scope/DB name/hostname
- ADR-0002 pnpm monorepo Next+Fastify+worker — PRD mandates modular monolith, versioned public API awkward in single Next 
- ADR-0003 Postgres RLS + app scoping — top risk is cross-tenant leakage; irreversible — FORCE RLS on current_setting, NOB
- ADR-0004 embedded-postgres — no Docker/root on dev machine; PGlite rejected too weak for concurrency evidence — port 543
- ADR-0005 strict opt-in consent all channels — D6 legal decision by product owner — single gate, no bypass, suppression r
- ADR-0006 Drizzle over Prisma — RLS-friendly typed access — NOTE: actual code uses raw `pg` + hand-written SQL via Tenant
- ADR-0007 own-tables auth, scrypt — D9 residency unresolved, vendor PII export would pre-decide it — opaque server-side s
- ADR-0008 segment conditions as stored AST compiled to parameterised SQL — no-code conditions + live counts — AST is the 
- ADR-0009 public/private split in one Next app with 4-layer anti-indexing — SEO-007 — route groups + edge/middleware head
- ADR-0010 composite foreign keys carry the tenant — raised by adversarial review after real cross-tenant WRITE + permanen
- ADR-0011 same-origin BFF web auth — reverses M1 recommendation on analysis; third-party-cookie future kills alternative 
- ADR-0012 Playwright browser E2E — two M1 defects hid behind HTTP-level testing (form pointing at nonexistent route; fabr
- ADR-0013 native CRM; external connector becomes later integration — target SMB shouldn't buy a second product; D4 blocke
- Assumption register A-01..A-09 with revisit triggers (incl. Redis/BullMQ deferred, dev-only tokens until EmailPort) — AR

## [[chat-agent-saas]]
- Zod-at-the-boundary validation** with per-module `*.schemas.ts` and a single `validateBody` middleware; error envelope n
- String permissions + org-owner bypass** instead of bitfield roles (`shared/constants/permissions.ts` ALL_PERMISSIONS, DE
- Status-as-plain-strings** across all models (no PG enums) — flexible for the operator-driven state machines (campaigns, 
- AES-256-GCM envelope via ENCRYPTION_KEY** for every tenant secret at rest (org/agent API keys, MCP headers, channel cred
- Turborepo+npm workspaces**, shared types package consumed by api/web/widget only (root `package.json`, per-package manif
- Express monolith + separate worker tier** split by `START_WORKERS`, sized for a ~900MB EC2 box (`ecosystem.config.cjs` h
- Gemini-first, real multi-provider routing** added later after discovering provider selection was cosmetic (`modelProvide
- pgvector hybrid retrieval (dense + simple + arabic, RRF k=60)** because dense-only misses exact lexical signals like SKU
- Verified-identity trust boundary**: `Conversation.externalUserId` documented UNTRUSTED vs `externalIdentityId` VERIFIED;
- Deny-by-default Odoo op-class permissions** replacing a single boolean, with documented deliberate security downgrade fo
- Custom-LLM voice path default-on** for new agents to reuse the text-chat brain and halve LLM hops, legacy path kept as a
- DB-backed SystemConfig with Redis pub/sub invalidation** (values never transit pub/sub — keys only, `config.ts:7-12`); m
- Per-key circuit breakers for embeddings** after one tenant's bulk ingest tripped a shared breaker (`embeddings.ts:56-63`
- Sync/async boundaries**: chat turns are synchronous HTTP/SSE end-to-end (no queue hop for the reply — webhook handlers c
- Early-ack webhook processing** (200 before work) trading at-most-once delivery for Meta retry-friendliness (`webhook-v2.
- Hardened deploy pipeline** with DROP-guard, snapshot, health gate (`deploy.sh` header citing PRODUCTION_READINESS_PLAN.m
- Shadow-DOM framework-free widget** (single script tag) and Next.js 16 frontends served by PM2 post-migration (`ecosystem

## [[cvm]]
- Modular monolith with enforced boundaries — monorepo risk of module spaghetti — dependency-cruiser 10 rules in CI (`pnpm
- TypeScript platform + Python strictly offline ML — avoid dual-language serving path — extraction and scoring stayed in T
- Fastify + Zod as single source of truth — schema drift between validation/docs/types — validator+serializer compilers, O
- Postgres is the only datastore — operational simplicity, transactional guarantees — even queues (pg-boss), outbox, idemp
- Tenant isolation triple-layered — cross-tenant leak is existential for enterprise — FORCEd RLS + restricted runtime role
- Transactional job enqueue — lost-work windows between write and job — pg-boss row commits atomically with domain row — A
- One PolicyGate, fail-closed, re-checked at send time — consent withdrawn after audience build is THE compliance failure 
- Rule AST is data, never SQL — injection + explainability + reuse across segments/eligibility/exclusions — closed field c
- Effectively-once delivery via DB uniqueness — provider duplicates are the classic CVM wound — claim-before-send on uniqu
- No client JavaScript in the console — density, RTL correctness, accessibility, CSP-friendly — RSC + server actions + URL
- Honesty conditions as release gates — credibility of an operator tool — no mock screens, synthetic labelled everywhere, 
- Feature definitions are data compiled to SQL; read/record split — lineage questions ("what did this number mean at decis
- API keys embed their tenant (new from implementation) — auth-time tenant scoping without lookup round-trip — docs/adr/01

## [[faraj]]
- Zero runtime/UI/state libraries: motion is CSS + IntersectionObserver (README.md:12-14; confirmed — deps are exactly nex
- Type-enforced bilingualism: `Localized<T>` makes missing translations uncompilable (src/lib/i18n.ts:9, README.md:73-77).
- Tailwind v4 CSS-first: theme in `@theme` instead of config file (globals.css:17; README.md:83-85).
- Next.js 16 `proxy.ts` over middleware for locale redirect (src/proxy.ts:7-8).
- Accessibility floors built-in: skip-link, noscript un-hide of reveals, focus-visible styles, AA contrast ratios annotate
- Latin display/body fonts served from Fontshare CDN @import; only Arabic self-hosted via next/font (globals.css:1, layout

## [[iscc-testing]]
- Extend, don't fork core Odoo models; new modules only at clear boundaries (README "Architecture rules").
- One violation engine; detectors delegate to `action_issue()`.
- Attendance sync cron ships inactive with a mock demo source — safe-by-default rollout.
- Payroll integration requires Enterprise `hr_payroll`; explicitly skipped on Community.
- Government reporting via CSV + manual upload because platforms lack open write APIs (flagged in code).
- Botify RPC: deny-by-default method allowlist, forbidden-method hard stop, limit cap 200, no deletion ever.

## [[luma]]
- Worker decoupled from storage via a single port + two adapters; default flipped from direct DB to Backend API mode (arch
- Multi-row atomicity pushed into coarse endpoints ("one request is one transaction"); lost races are `200 {"applied": fal
- Lease fencing token `(worker_id, lease_generation)` set atomically at claim and re-verified at renew/settle to neutraliz
- Schema ownership split: BE owns platform schema; ai-engine maintains a runnable worker-scoped subset, coordinated via do
- Graceful degradation: failed upstream dependency blocks transitive downstream except Knuth, which compiles an explicitly
- CAS booleans over exceptions for race-prone queue operations.
- Council config lives in DB (agent_definitions seeded, execution_order 1..11), not code — prompts editable without deploy
- Deliberate gaps accepted and documented: debate coordinator not yet wired into generate path; provider failover health p
- Deployment simplicity: Docker Compose + PM2, Postgres kept on host outside compose (README).

## [[mawid-ai]]
- One-way package graph web→ai→backend→core — AI tools call the booking domain, so agent-driving orchestrators were placed
- Plain agent loop, no intent regexes — five regex routing/synthesis layers were deleted; model decides tools; the ONLY se
- Per-org encrypted tokens over shared token — tenants onboard asynchronously; compromise blast-radius contained; AES-GCM 
- Manual Cloud-API connect as the only WhatsApp path — Embedded Signup deleted (owner request), QR/Baileys banned (ToS); s (`303531b`)
- Server never builds — EC2 too small for next build; CI+GHCR pull-only deploy with sha-tagged images for instant rollback (`d86a1cb`)
- Hand-written idempotent SQL migrations for prod — drizzle-kit push reserved for dev; avoids destructive auto-migrations 
- Payments opt-in at two gates — STRIPE_SECRET_KEY env AND platform_settings.payments_enabled, flag injected INTO the doma
- Test-enforced OpenAPI without codegen — static public/openapi.json + parity test + CDN Swagger UI page — evidence: commi (`1019517`)
- Hosted-URL desktop shell (v1) — zero local backend, same cookies/CORS as browser tab; secure token storage deferred to h
- Cron-as-endpoint with DB-held secret — platform_settings.cron_secret + header auth + 503-if-unconfigured fail-closed pos

## [[mythos]]
- Fork-and-rebrand Hermes as SaaS** — context: wanted productized self-improving agent w/o BYO-keys — decision: fork v0.13 (`027c668`)
- Zero telemetry egress** — context: upstream partly a training-data pipeline — decision: strip every egress path (traject
- Local agent + cloud brain trust split** — device holds only session token; provider keys server-side only; single-tenant
- Filesystem sandbox is dual-layer** — OS-level isolation + app-layer pathguard shipped together, neither alone — evidence
- Plugin surface instead of core edits** — context: hardcoded honcho argparse in main.py — decision: expand generic hooks/
- Prompt-cache preservation over freshness** — slash commands mutating system-prompt state default to deferred invalidatio
- Dashboard embeds the real TUI** — no second chat implementation in React; PTY bridge carries `safa --tui` to xterm.js — 
- Hermetic test wrapper** — context: repeated works-locally-fails-CI incidents — decision: scripts/run_tests.sh normalizes
- Lazy provider-plugin discovery separate from PluginManager** — avoids double ProviderProfile instantiation; user plugins

## [[sham-v2]]
- Full schema map in every prompt instead of retrieval (~64KB stable prefix exploits provider context caching) — README.md
- Model outputs only {in_scope, sql, title_ar}; refusal/clarification/humanized text all deterministic-or-validated in cod
- Physical exclusion of secret/personal columns at build time (NEVER_COPY_COLUMNS) as primary defense; guard as second lay
- Immutable generations + atomic pointer swap + graceful restart, instead of migrating a live DB.
- Channel-neutral queues (inbound_events/delivery_outbox) rather than WhatsApp-specific tables (runtime/db.js:8-13).
- Zero-row review round + "EMPTY is an answer" doctrine prevents invented results (measured: zero hallucinated-field failu
- Hand-rolled core utils (LRU/semaphore/single-flight/metrics) instead of deps — matches "small on purpose".

## [[shamsieh]]
- Keep payroll modules removable via uninstall-me stubs rather than breaking Odoo.sh upgrades.
- Deny-by-default Botify policy manifest with explicit, commit-recorded operator decisions for each opened model.
- Device integrations live outside Odoo (FastAPI bridges) because Odoo.sh cannot reach LAN devices; durable SQLite queue b
- Consolidate WFH/overtime/hourly departures onto the native Time Off engine.
- Arabic-first UX: dedicated professional translation module plus generated PO tooling.
- Raw payload retention is temporary by design (purge cron).

## [[telvora]]
- Modular monolith, not microservices — spec warned against premature decomposition; only ml split out for runtime needs; 
- Pooled tenancy + FORCE RLS as primary control, defended in depth (middleware-set GUC, worker role trust boundary, tenant
- Storage split with deliberate omissions (no ClickHouse/Snowflake; Athena-over-S3 planned, not built locally; Valkey disp
- Honest local adapters over emulators: RawStore/Queue/Stream interfaces with filesystem/Postgres implementations matching
- Self-service signup reuses invite-accept verbatim (password collected on accept screen, sandbox-only label, reused rate 
- Production topology honest about actual implementation: RDS (not Aurora) because PG18 uuidv7 + CDK engine gap; EFS for f
- Deterministic real-time path: LLMs never in the decision loop; they draft/explain only, behind typed read-only tools + p
- Phase-ordered agent build (B00→B41, exit-gated, contradiction-resolution rule) as the execution contract — AGENT_BUILD_P

## [[test-ai]]
- Deterministic-first architecture: model calls reserved for planning prose and answer prose; everything else is code, YAM
- Security by construction: ai_reader + views + parameterized SQL + statement timeout + output number-guard + method-free 
- No AWS SDK: 40 lines of SigV4 hmac instead of boto3's 50MB dependency (refresh.py docstring).
- Named static asset routes instead of parameterized `/{asset}` (api.py comment documents the rejection).
- Rollback net + frozen stable branch + `[loop]` commit prefix as process technology.
- Country scoping defaults to global search rather than erroring when unknown.
- Tests fail loudly when infrastructure is missing (node notice) — "a security check that quietly stops running is worse t

## [[umbrellaprime]]
- Static export + S3/CloudFront/OAC over a Node server (or Vercel): cheapest Saudi-friendly hosting; accepted cost is losi
- Edge-rewrites instead of S3 website endpoint: keeps bucket private (AWS-recommended OAC pattern), at the price of needin
- Client-side root redirect with triple fallback (script/meta-refresh/manual links) since no server-side Accept-Language n
- One Zod schema builder parameterized by localized messages; Lambda keeps a deliberately looser English-only schema as pu
- Honest-state UX: form refuses to claim success unless Lambda confirms; missing config renders as explicit state, not sil
- Honeypot over captcha; clip-based hiding after off-canvas caused overflow (ContactForm.tsx:87-91).
- brand-source/ kept on disk but gitignored — originals preserved, derivatives committed (README.md:58-66).
- sharp/postcss version overrides + allowScripts pinning in package.json.
