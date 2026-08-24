# CORTEX REPORT — sham-v2 (شمسي / Shamsi)

## META
project_id: sham-v2
root: /home/aboud/Dev/sham-v2
kind: Node.js backend service — Arabic-language Q&A agent over an education catalog, answering via WhatsApp + HTTP API (Gemini → guarded SQL → grounded answers)
languages: JavaScript (ESM, "type":"module"), ~68 js files
frameworks: Express 5 · better-sqlite3 12 · @google/genai (Gemini) · zod · pino · node-cron · helmet/express-rate-limit/cors
package_managers: npm (package-lock.json)
test_frameworks: Node built-in test runner (`node --test`) + custom offline/live eval harness (593 cases)
deployment: PM2 on a VPS (ecosystem.config.cjs; docs/API.md names https://apr365.com), `scripts/deploy.sh dry|go`, daily S3 backup sync via node-cron scheduler; storage/ and .env gitignored by policy
note: the task brief guessed "fee/comparison tool" [inferred from name only] — actually an education-directory agent (institutions/teachers/specialties in Jordan); fee/comparison questions are one supported question class (`COMPARISON_CRITERIA`)

## OVERVIEW
Shamsi ("شمسي") is a WhatsApp + HTTP API agent that answers questions about educational institutions, teachers, and specialties in Jordan. Its governing principle (README.md:5-6): **Gemini translates the question to SQL; the database alone produces facts; code verifies before anything is said.** The model writes one SELECT plus an Arabic title and nothing else — every number/name in the final answer must come from a query row (src/agent/index.js:9-16). Out-of-scope/refusal text is rendered deterministically in code, never authored by the model (src/agent/render.js per AGENTS.md).

The pipeline is a single path for all channels: question → Gemini structured plan (`{in_scope, title_ar, sql, reason}`, src/agent/index.js:95-118) with the *entire* schema map (~64KB, all 38 tables/612 columns with real values, JSON shapes, ranges) in every prompt → multi-layer SQL guard (src/agent/guard.js) → readonly execution in a worker thread (src/agent/execute.js) → deterministic Arabic rendering of rows. Zero rows is a legitimate verified answer ("EMPTY is an answer, not a failure") but gets one review round before being stated (index.js:507-521).

Data comes in as PostgreSQL dump backups (PGDMP) that are imported into immutable SQLite "catalog generations", swapped atomically via an `active.json` pointer, opened `readonly + query_only` (src/db/catalog.js:1-56). All mutable state lives in a separate runtime SQLite DB (sessions, inbound inbox, delivery outbox, workflow instances — src/runtime/db.js). Measured quality: 107/108 (99.1%) on natural-language eval suite at generation 20260802073931-… (README.md:115-127).

## ARCHITECTURE
Layered, deliberately small ("small on purpose: one question path, two channels" — AGENTS.md):
- **channels/** = thin adapters only, no business logic: HTTP (src/channels/http/, src/app.js) and WhatsApp (src/channels/whatsapp/ — webhook → persist → worker consumes queue → outbox).
- **agent/** = "the single place for logic" (README.md map): plan/guard/execute/render/humanize/clarify/ranking/guided.
- **db/** = generation machinery: catalog connection+pointer, schema profiling, semantics layer, mirror builder, PGDMP import (src/db/, src/sync/).
- **runtime/** = operational state: sessions, outbox, workflow engine (institution/teacher verification flows), runtime DB.
- **core/** = hand-rolled primitives: LRU, semaphore, single-flight, metrics, Arabic normalization, custom SQLite functions (`norm_ar`/`like_ar`/`name_like_ar`, src/core/sql-functions.js registered in catalog.js:58-60).
Critical ordering documented in src/app.js:4-7 & 57-66: the WhatsApp webhook is registered BEFORE express.json because signature verification needs the raw body.

## MODULES

### agent-core — ask() pipeline
purpose: one path from any channel's question to a grounded Arabic answer.
path_prefixes: src/agent/index.js, src/agent/prompt.js, src/agent/gemini.js
key_files: src/agent/index.js:350-586 (`ask()` main loop), index.js:303-334 (`plan()` structured call, temperature 0, maxOutputTokens 8192), index.js:442-565 (repair loop: max 3 deterministic repairs, provider 504/429 retries don't consume repair rounds), index.js:126-133 (LRU answer cache keyed per generation)
entrypoints: `ask(question, options)` — called by HTTP controller, WhatsApp worker, voice channel
responsibilities: scope decision, SQL generation w/ full-schema prompt, zero-row review round, humanize pass over the same rows (fallback to deterministic text if model fails), time-budget management (deadline + remaining() guards everywhere)
invariants: model never authors facts; EMPTY(verified_zero) survives later failures (index.js:567-572); cache key includes activeGeneration() so stale-generation answers can't leak (index.js:384)
pitfalls: many narrow regex intent-detectors hardcoded here (reviewer privacy, teacher-affiliation count, near-me intent — index.js:47-66,136) — each is product logic living in the pipeline file
confidence: high

### sql-guard — query validation & sandboxed execution
purpose: reject unsafe/wrong SQL before execution; run it isolated.
path_prefixes: src/agent/guard.js, src/agent/execute.js, src/agent/worker.js
key_files: guard.js:317-447 (`validateSql` — 6 layers: literal stripping/keyword ban → SQLite prepare → stmt.readonly verdict → output-column source attribution for sensitive fields → FROM/JOIN table allowlist → EXPLAIN QUERY PLAN cost cap of 1e7 estimated row visits); guard.js:66-82 (bans non-ASCII literal comparisons — Arabic hamza variants silently return 0 rows; forces `like_ar()`); execute.js:25-74 (per-query Worker thread w/ resource limits, timeout kills without waiting on terminate, leakedWorkers counter)
entrypoints: `runSql(sql, {allowContact,...})` (execute.js:130-183) — the ONLY execution door
responsibilities: contact columns blocked unless user explicitly asked (`allowContact`); entity-name-without-id rule so UI can deep-link rows (guard.js:396-407); LIMIT injection; cell truncation; redacted SQL logging
invariants: every query passes guard.js (AGENTS.md constant); sensitive columns physically absent from the file anyway (semantics NEVER_COPY_COLUMNS) — guard is defense-in-depth layer 2
pitfalls: heavy regex-on-SQL layers are bypassable in principle (acknowledged in guard.js header: "the parser being SQLite itself" is the real wall); leaked workers metric is the ops alarm (execute.js:185-186)
confidence: high

### db-generation — catalog generations & semantic layer
purpose: build immutable readonly SQLite catalogs from PGDMP backups; describe every column to the model.
path_prefixes: src/db/{catalog,pointer,schema,semantics,mirror,build}.js
key_files: catalog.js:36-56 (serving vs build mode; `query_only=ON`; explicit startup error not silent empty DB); semantics.js:14-60 (SENSITIVITY policy public/on_request/hidden/never + NEVER_COPY_COLUMNS physical exclusion of passwords/tokens/DOB etc.); schema.js (auto-profiling: types, JSON keys, enumerated values, row counts — feeds the 64KB prompt)
entrypoints: `npm run sync` (src/db/build.js); pointer swap via active.json
responsibilities: atomic generation swap triggers graceful restart when CATALOG_RESTART_ON_ACTIVATION set (src/server.js:62-67); derived tables institutions/teachers/posts created in build mode (catalog.js:79-142)
invariants: serving DB never written (readonly+query_only); internal tables marked exposure=internal aren't copied at all (semantics.js:20-21)
pitfalls: pg_restore required to build new generations (ships prebuilt so check works offline); don't touch storage/catalogs manually (AGENTS.md)
confidence: high

### channels-http — API surface
purpose: thin REST adapter; session hygiene; admin-only SQL disclosure.
path_prefixes: src/app.js, src/channels/http/
key_files: app.js:70-77 (routes); chat.controller.js:102-174 (POST /api/chat — sanitizes session id, reserves `wa_` prefix for WhatsApp, merges sanitized user profile {name, location}, caps history at 8 turns); chat.controller.js:169 (sql/attempts/ms only returned when req.isAdmin)
entrypoints: npm start → src/server.js → app.listen
responsibilities: rate limiting (chatLimiter), CORS allowlist from env (shamsieh.education/apr365.com per docs/API.md), helmet, trust-proxy config
invariants: channel identity never read from request body (AGENTS.md); raw-body webhook ordering (app.js:57-66)
confidence: high

### channels-whatsapp — Meta webhook + queue worker
purpose: receive, dedupe, and answer WhatsApp traffic; media/voice support.
path_prefixes: src/channels/whatsapp/, src/channels/voice.js
key_files: webhook.js:31-55 (signature verify on RAW body → phone_number_id match → persistInbound → 200 immediately; processing never inline or Meta re-delivers 5×); worker.js (routing is two lines: active workflow? transition : ask(); everything sent via outbox for ordering/dedupe/retry); meta-client.js (signature/challenge/send); media.js (voice transcription/TTS)
entrypoints: POST/GET /api/webhooks/whatsapp
responsibilities: verification workflows (institution/teacher) driven through same worker; voice channel reuses the same ask() core (commit 4df74e2)
invariants: all inbound via inbox (provider_message_id PK = permanent dedupe, runtime/db.js:61-77); all outbound via delivery_outbox with idempotency_key UNIQUE (runtime/db.js:80-101)
confidence: high

### runtime-state — sessions, workflows, outbox
purpose: everything that must survive catalog swaps, in its own WAL SQLite DB.
path_prefixes: src/runtime/
key_files: runtime/db.js:30-141 (schema v1: sessions w/ optimistic revision counter, user_profiles, inbound_events, delivery_outbox, workflow_instances+workflow_events append-only audit); db.js:143-197 (additive repeatable migrations — add-missing-columns only, never drop); workflow-engine.js / teacher-verification.js / institution-verification.js
entrypoints: imported by server shutdown (saveAllSessions) and both workers
responsibilities: state derived from event history so audits answer "why did this instance reach this state"
invariants: catalog DB and runtime DB are separate files by design (runtime/db.js:1-15)
pitfalls: no data migration story across environments except manual SQLite copy after stop (documented in header comment)
confidence: high

### sync-eval — PGDMP import pipeline & accuracy harness
purpose: rebuild catalogs from S3-fetched backups nightly; measure answer correctness continuously.
path_prefixes: src/sync/, test/eval/
key_files: sync/pg-backup.js, sync/import-backup.js, sync/scheduler.js (node-cron; commit 3650fed closed the last manual data path); test/eval/run.js + cases-schema.js (488 cases GENERATED from the schema map itself — coverage grows with new columns) + cases-natural.js (105 handwritten dialect cases incl. expected refusals); ground truth computed by executing reference queries on the same file, compared on ROWS not prose (README.md:94-113)
entrypoints: `npm run eval [-- --suite|--id]`, failures land in test/eval/failures.json
responsibilities: regression gate — "any new eval failure is a regression; fix it or explain the expectation change in the same commit" (AGENTS.md)
confidence: high

## FLOWS

### API chat question
trigger: POST /api/chat {message, session_id?, allow_contact?, user?}.
steps: rate-limit → sanitize session/profile → clarify gate (`decideClarification` fires BEFORE any model call for ambiguous superlatives, asks exactly once, then defaults — index.js:363-377) → ranking-intent fast path answers clean measured-preference questions deterministically without Gemini (index.js:423-426) → LRU cache hit? return → Gemini plan → validateSql → zero rows? one review round → execute → renderAnswer (+ optional humanize) → finish() prefixes assumed-criterion disclosure → save history, respond (SQL shown to admins only).
files: src/channels/http/chat.controller.js, src/agent/index.js, src/agent/guard.js, src/agent/execute.js, src/agent/render.js, src/agent/clarify.js
confidence: high

### WhatsApp inbound message
trigger: Meta webhook POST.
steps: raw-body HMAC verify → phone_number_id match → normalizeWebhook → INSERT into inbound_events (PK dedupe) → 200 within Meta's window → worker claims batch → routes: active workflow transition OR ask() → deliveries enqueued to delivery_outbox with idempotency keys → sender delivers to Graph API with retry/backoff.
files: src/channels/whatsapp/webhook.js, inbound.js, worker.js, delivery.js; src/runtime/outbox.js
confidence: high

### Catalog sync / generation swap
trigger: cron scheduler pulls PGDMP backup (or manual `npm run sync`).
steps: build-mode staging DB opened writable → import-backup restores via pg_restore → mirror builds relational tables → schema profiles rebuilt → activate: atomic pointer write → running service detects activation → graceful self-restart (SIGTERM-like shutdown flushes sessions/runtime first, server.js:33-57) → next boot opens new generation readonly.
files: src/db/build.js, src/db/pointer.js, src/sync/{pg-backup,import-backup,scheduler}.js, src/server.js
confidence: high

### Guided school search (API only)
trigger: parent mentions child + school intent (regex-gated, index.js:208-215).
steps: startGuidedSchool collects city/budget/system/child-gender → buildGuidedSchoolSql constructs parameterized-by-code SQL from the plan (never the model) → runSql through normal guard → top-3 rendered with institution action links + seat-booking follow-up.
files: src/agent/index.js:220-301, src/agent/guided.js, src/channels/http/chat.controller.js:91-140
confidence: high

## APIS
Base https://apr365.com (docs/API.md); 60 req/min/IP; uniform error shape `{error, error_code}`.

| Method | Path | Purpose | Evidence |
|---|---|---|---|
| POST | /api/chat | main Q&A (message ≤1000 chars; session continuity; admin sees sql/attempts/ms) | src/app.js:70, src/channels/http/chat.controller.js |
| GET/POST | /api/webhooks/whatsapp | Meta verification challenge / signed webhook | src/app.js:58,75 |
| POST | /api/voice/tools/ask | voice tool entry, static-secret protected | src/app.js:72 |
| GET | /api/voice/auth | signed URL for voice client | src/app.js:73 |
| GET | /api/voice/status | voice capability status | src/app.js:74 |
| GET | /api/config | public config | src/app.js:76 |
| GET | /api/health | health/liveness | src/app.js:77 |

## DATABASE
Three distinct stores:
1. **Catalog (product data)**: SQLite file per generation under storage/catalogs/, opened `readonly + query_only`; source of truth is PostgreSQL PGDMP backup files (storage/*.sql, fetched from S3 nightly). Schema map: 38 tables / 612 columns / 112 JSON-shaped columns (README.md:38-46).
2. **Runtime DB**: storage/runtime.sqlite (WAL) — sessions, user_profiles, inbound_events, delivery_outbox, workflow_* tables.
3. **No ORM** — better-sqlite3 prepared statements throughout; custom Arabic collation functions registered on both connections.

## TESTS
- Framework: Node built-in test runner. Command: `npm test` (node --test test/*.test.js); 10 suites in test/: agent, clarify, entity-type, grounding, guided, guided-http, ranking, render-actions, runtime.
- Gate: `npm run check` = eslint + tests + offline eval checks (no network needed; ships prebuilt generation).
- Accuracy harness: `npm run eval` (needs Gemini key; 593 cases ≈20min), `eval:offline`; failures dumped to test/eval/failures.json with generated SQL.
- Ops scripts: scripts/deploy.sh (dry/go), scripts/ask.js (first-line diagnostic tool), scripts/schema.js (inspect what the model sees).

## GIT LESSONS
~79 commits, Arabic conventional-ish messages, main branch + feat/* branches, PR #4 merged (555218a). Current tree dirty (agent/* files modified).
- **v5 rewrite deleted everything else**: commit 05780fe "مسار واحد مؤرَّض بالـSQL، وحذف كل ما عداه" — replaced a parallel search/embedding architecture with the single SQL-grounded path; later commits removed semantic caches (fbbc557) and embeddings (27dfc6b "قيود مُتحقَّن منها بدل تشابه دلالي"). Lesson: retrieval similarity was hiding the column holding the answer; grounding won measurably.
- **Counting-vs-price class of bugs** fixed repeatedly (5dca342 "العدّ ليس جوابًا لسؤال سعري", c7f6709 named-school question answered with a count, a39694f university-specialty question returned Quran centers) → led to the deterministic COMPARISON_CRITERIA + clarify/ranking override design (71fbe7e, HEAD).
- **Voice channel consolidation**: 4df74e2 gave voice the same chat core instead of a weaker second brain.
- **Ops honesty commits**: fb250ed/54d82f5 record production latency measurement methodology and cleanup rules in docs.
- Generation-cleaner hardening (e448757) chases orphan -shm/-wal files — filesystem-level lessons about atomic swaps.

## DECISIONS
- Full schema map in every prompt instead of retrieval (~64KB stable prefix exploits provider context caching) — README.md:38-40.
- Model outputs only {in_scope, sql, title_ar}; refusal/clarification/humanized text all deterministic-or-validated in code.
- Physical exclusion of secret/personal columns at build time (NEVER_COPY_COLUMNS) as primary defense; guard as second layer.
- Immutable generations + atomic pointer swap + graceful restart, instead of migrating a live DB.
- Channel-neutral queues (inbound_events/delivery_outbox) rather than WhatsApp-specific tables (runtime/db.js:8-13).
- Zero-row review round + "EMPTY is an answer" doctrine prevents invented results (measured: zero hallucinated-field failures in last eval, README.md:127).
- Hand-rolled core utils (LRU/semaphore/single-flight/metrics) instead of deps — matches "small on purpose".

## RISKS & TECH DEBT
- Working tree currently dirty across src/agent/* — uncommitted changes to the most critical files.
- Guard relies partly on regex SQL inspection; safe today because the DB itself is readonly and sensitive columns don't exist, but each new bypass pattern is whack-a-mole (self-acknowledged).
- Intent-detection regexes accumulate in agent/index.js (privacy, affiliation-count, near-me, child-guided) — growing special-case surface outside the declared "facts live in semantics.js" rule.
- In-process LRU cache + metrics lost on restart; single fork instance (PM2 instances:1) — throughput ceiling by design (500MB box budget).
- Leaked-worker counter exists because terminated workers stuck in sync SQLite calls can't be reclaimed — sustained timeouts would degrade capacity until restart.
- storage/ excluded from git; disaster recovery depends entirely on push-backup.sh discipline and S3 retention.
- README documents eval numbers against a specific generation; numbers rot as generations advance unless re-measured.

## UNCERTAIN
- Exact production host topology beyond "PM2 VPS + apr365.com domain" [inferred from ecosystem.config.cjs + docs/API.md]; deploy.sh internals not read.
- src/integrations/shamsi-admin.js and parts of voice.js/media.js not examined in detail [uncertain].
- Whether WhatsApp number/Meta app config in .env.example reflects current production credentials [uncertain].
- Eval figures quoted from README (99.1% NL) could not be independently re-run (needs Gemini key) [reported, unverified].
