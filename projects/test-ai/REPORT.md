# CORTEX REPORT — TEST AI

## META
project_id: test-ai
root: /home/aboud/Dev/TEST AI
kind: Arabic-first LLM question-answering agent over a curated PostgreSQL education directory (the "Botify" backend serving the Shamsieh org), with WhatsApp + voice + web channels and an ops dashboard
languages: Python, JavaScript (vanilla web/dashboard), SQL (views/functions/roles), YAML (catalog), Bash/Make
frameworks: FastAPI + uvicorn, psycopg 3 (pool), httpx, Pydantic, ElevenLabs custom-LLM voice, Meta WhatsApp Cloud API, Google Gemini API
package_managers: pip (requirements.txt, 6 deps); Makefile as task runner; ./setup.sh bootstrap
test_frameworks: plain-python assert files with shared tests/_runner.py + one node file for XSS; custom eval harness (golden set + LLM judge)
deployment: systemd oneshot service + timer (`deploy/shamsieh-refresh.{service,timer}`) at /opt/shamsieh-agent for nightly S3 backup restore; uvicorn behind public HTTPS for WhatsApp/ElevenLabs webhooks; dev DB via docker container `shamsieh-db`

## OVERVIEW

TEST AI is the Shamsieh Education Agent (وكيل شمسية التعليمي): it answers questions — in Arabic, English, or any language the user writes — about Jordan's private education directory (schools, kindergartens, daycares, universities, teachers, special-needs centers, housing, other places). Its users are families mid-decision, arriving by phone call, WhatsApp, or web chat in Jordanian Arabic full of speech-recognition noise; the operator is one product owner monitoring a diagnostic dashboard (PRODUCT.md).

The central design principle is stated in README.md: **Gemini never writes SQL.** The model emits a structured QuerySpec; deterministic code compiles it to parameterized SQL over curated `ai_views`; a second model writes the answer *only from a fact sheet* — it never sees schema, SQL, or raw rows — and an output guard rejects any number that cannot be traced back to that fact sheet. The pipeline is deliberately deterministic-first: normalization, domain routing (8 domains), entity resolution, and count-question fast paths all run without any model call; the normal path costs exactly two Gemini calls, refusals/clarifications one, fast-path zero.

The repo doubles as an evaluation laboratory: eleven audit scripts check whole classes of defects (enum vocabulary vs real column values, unreachable source columns, name-resolution round-trips over 4,220 names, filter-combination execution across 555 declared combos, view materialization of every cell, claim-number honesty regenerated from data), and a logbook + LLM judge measure wrong-answer rates from production traffic with Wilson intervals. Work proceeds in "[loop]" hardening rounds against a tagged stable point, with rollback documented in LOOP.md.

## ARCHITECTURE

Request lifecycle (agent/pipeline.py): `normalize → resolve → route → plan → validate → compile → execute → compute → generate → guard → emit → trace`.

- Entry points: `agent/cli.py` (interactive REPL, `make run`), `agent/api.py:app` (FastAPI, `make api`; same process serves WhatsApp webhook `/whatsapp` [inferred route] and ElevenLabs `/voice/chat/completions` custom-LLM endpoint), `python -m agent.refresh` (nightly S3 restore under systemd).
- Data plane: PostgreSQL container `shamsieh-db`, database `shamsieh`; read layer = ~66 views (32 core in sql/01_views.sql + 17 coverage + 17 filters) behind read-only role `ai_reader` with 3s statement timeout; `unaccent_ar()` + trigram indexes (sql/00_functions.sql).
- Semantic layer: `catalog/*.yaml` — labels (Arabic enum names), ~250 aliases, geo hierarchy/bounds, policy gates & absent entities & fee units, per-domain field specs in catalog/domains/*.yaml.
- Scheduled job: systemd timer 03:30 Asia/Amman runs agent.refresh — SigV4-signed S3 LIST+GET (hand-rolled hmac, explicitly no boto3), age/size/ETag guards, download, restore into scratch DB, row-count verify, apply views, atomic swap; Restart=on-failure every 15 min, burst 4 ("past that it's not a late dump, it's a broken one").
- Channels: WhatsApp Cloud (HMAC signature verify, message splitting ≤3900 chars, list messages, media download); ElevenLabs voice (speech-normalized text: digits spelled, hosts spelled, internal notes suppressed, row cap 3); web chat (web/index.html) + dashboard instrument panel (web/dashboard*).
- Ops surfaces: /traces, /stats, /dashboard, /reports/notes|voice (admin-key guarded), user problem reports POST /report with rate limit + image sniffing.

## MODULES

### pipeline-core — request lifecycle
purpose: Orchestrate one turn end-to-end with outcome classification (answered/smalltalk/refused/clarified/plan_failed).
path_prefixes: agent/pipeline.py, agent/session.py, agent/intake.py, agent/smalltalk.py
key_files: agent/pipeline.py (Agent.ask, TurnResult)
entrypoints: called by api.py, cli.py, whatsapp.py, voice.py
responsibilities: session context carrying location/country/last entities; clarification handling; timings + token usage capture.
invariants: two Gemini calls max on normal path; zero-model fast path preserved.
confidence: high

### arabic-lang — language understanding without a model
purpose: Arabic normalization, language detection, synonym/respelling tolerance.
path_prefixes: agent/arabic.py, agent/lang.py
key_files: agent/arabic.py (normalize), agent/lang.py
entrypoints: first stage of every turn
responsibilities: normalize alef/ya/taa-marbuta/diacritics parity with SQL `unaccent_ar` (audit checks equality on 4,220 names); detect language; guard gradations.
pitfalls: normalization drift between Python and SQL silently breaks name resolution — hence the standing audit.
confidence: high

### routing-resolution — deterministic domain routing + entity resolution
purpose: Map a question to one of 8 domains and resolve mentioned places/institutions with thresholds instead of guessing.
path_prefixes: agent/router.py, agent/resolve.py, agent/country.py, catalog/aliases.yaml, catalog/geo.yaml
key_files: agent/resolve.py (threshold 0.75, margin 0.10 → KNOWN_ABSENT / NOT_FOUND / AMBIGUOUS), agent/country.py (country via user.countryId → proxy header → server-side IP lookup → unscoped-by-design)
entrypoints: stages 2–3 of the pipeline
invariants: "non-scoped search is not an error, it's a deliberate default" (API.md); empty answers must say where the thing is (e8685eb).
confidence: high

### plan-compile-execute — QuerySpec engine
purpose: Turn natural language into safe parameterized SQL via structured spec + deterministic validator/compiler.
path_prefixes: agent/spec.py, agent/plan.py, agent/compile.py, agent/constraints.py, agent/fastpath.py, agent/db.py
key_files: agent/plan.py (planner Gemini call #1 + 9-check validator with ≤1 repair), agent/compile.py (QuerySpec→SQL; NULLS LAST, coverage denominators, filter semantics), sql/02_role.sql (ai_reader read-only)
entrypoints: pipeline stages 4–7
invariants: parameterized SQL only, executed as ai_reader on ai_views with statement_timeout=3s; validator may fix once, then refuses.
pitfalls: wildcard holes and near-miss entity matching were both historical bug families (commits 3d044cd, 03166a5) — audits now hunt classes, not instances.
confidence: high

### facts-answer-guard — honest numbers out
purpose: Compute everything deterministically, render the answer from a fact sheet only, and reject invented figures.
path_prefixes: agent/facts.py, agent/answer.py, agent/suggestions.py
key_files: agent/facts.py (all arithmetic + coverage denominator), agent/answer.py (Gemini call #2 + output guard)
invariants: every number in output must trace to the fact sheet; "a measured zero is not a warning" — honest-looking zeros were a hunted bug class (1dc16c3, 699008b).
confidence: high

### channels — whatsapp / voice / web
purpose: Carry the agent to users where they already are.
path_prefixes: agent/whatsapp.py, agent/voice.py, agent/voicesync.py, web/
key_files: agent/whatsapp.py (signature verify, split_message, send_list, media download), agent/voice.py (to_speech transformations, key verify, streaming chunks), web/index.html + dashboard files
entrypoints: FastAPI routes; static pages served by named routes (parameterized asset route was rejected deliberately — api.py comment)
pitfalls: markdown tables don't survive WhatsApp — converted; RTL broke drawer positioning on mobile (75446e2); greeting injected mid-call was a defect (0417f89).
confidence: high

### refresh — nightly data swap
purpose: Restore the freshest verified directory dump from S3 without ever applying the same file twice.
path_prefixes: agent/refresh.py, deploy/
key_files: agent/refresh.py (_sign/_signed_headers SigV4, select_backup age+size+ETag+name-pattern guards, restore_into scratch, verify counts, apply_views, swap), deploy/shamsieh-refresh.timer
entrypoints: `python -m agent.refresh` (systemd oneshot, Persistent=true timer)
invariants: idempotent via ETag comparison against last applied; never creates the DB implicitly; four retries then page.
confidence: high

### institution-verify — ops-through-conversation
purpose: Let staff verify institutions/teachers through WhatsApp flows backed by the Shamsieh admin API.
path_prefixes: agent/institution_verify.py
key_files: agent/institution_verify.py (login → JWT, pending_requests, create_upload_url → S3 put image, file_evidence, set_whatsapp_number, teacher verification)
entrypoints: triggered by intent phrases (wants_verify/wants_teacher_verify/menu/cancel)
responsibilities: evidence upload, WhatsApp number capture with phone normalization.
confidence: medium-high

### observability — trace / logbook / judge / dashboard
purpose: Record every turn, classify outcomes, judge correctness from production traffic, surface it all in a six-section two-language dashboard.
path_prefixes: agent/trace.py, agent/logbook.py, agent/judge.py, agent/reports.py, traces/, web/dashboard*
key_files: agent/logbook.py (SQLite logbook.db: sessions, turns, failures, top questions, unanswered, problems), agent/judge.py (LLM-judged strata, Wilson intervals), eval/run_eval.py (166 golden cases, concurrency 5, truth from SQL)
entrypoints: /dashboard, /traces, /stats, /reports/* (admin key)
invariants: eval traffic excluded from production stats (`_scope(include_eval)`).
confidence: high

### audits — class-level defect hunters
purpose: One script per bug family so regressions are caught by category, not by incident report.
path_prefixes: tools/audit_*.py
key_files: audit_enums (declared vocab vs column reality), audit_coverage (unreachable source columns), audit_resolution (every place finds itself), audit_vocab (substring collisions), audit_aliases (dangling synonyms), audit_claims (--fix regenerates claimed numbers from data), audit_filters (execute every field×op combo), audit_views (materialize every cell), audit_robustness (40 garbled questions + 13 adversarial plans), audit_semantics (fields narrower than the questions that attract them), audit_school_filters
confidence: high

## FLOWS

### ask-turn (web/api)
trigger: POST /ask {question, session_id?, lat/lon?, user.countryId?}
steps: country resolution → normalize → resolve entities (short-circuit KNOWN_ABSENT/NOT_FOUND/AMBIGUOUS with one Gemini clarify) → route domain → fastpath (count questions: zero LLM) else plan(QuerySpec) → validate(9 checks) → compile → execute as ai_reader → facts compute → answer generate from fact sheet → number-guard → suggestions generated in same call → trace recorded → response {answer, outcome, institutions[], suggestions[], trace_id, latency_ms, tokens}.
files: agent/pipeline.py, agent/plan.py, agent/compile.py, agent/facts.py, agent/answer.py, agent/api.py
confidence: high

### whatsapp-turn
trigger: Meta webhook POST with X-Hub-Signature-256
steps: HMAC verify against WHATSAPP_APP_SECRET → parse messages → session mapped from wa_id → same Agent.ask → text transformed (tables→WhatsApp formatting, split ≤3900) → Graph API send + mark_read; unsupported types get localized notice; voice notes/media handled or politely refused.
files: agent/whatsapp.py, agent/api.py
confidence: high

### voice-call
trigger: ElevenLabs Conversational AI calls /voice/chat/completions (custom LLM) with VOICE_API_KEY header
steps: derive question + session from payload → Agent.ask → fact sheet trimmed to SPOKEN_ROWS(3) → digits/domains spelled, internal notes dropped, greeting suppression rule → SSE chunks streamed back; voicesync keeps ElevenLags agent config aligned via tools/voice_setup.py.
files: agent/voice.py, agent/voicesync.py, tools/voice_setup.py
confidence: high

### nightly-directory-refresh
trigger: systemd timer 03:30 Asia/Amman (dump produced 03:00)
steps: LIST bucket (SigV4 signed query) → pick newest passing pattern/age(≥30min)/size(≥50MB) → ETag ≠ last applied else exit idempotently → stream download → restore into scratch DB → verify row counts → apply views/functions → atomic swap live↔scratch.
files: agent/refresh.py, deploy/shamsieh-refresh.service, deploy/shamsieh-refresh.timer
confidence: high

### problem-report
trigger: POST /report from web UI
steps: rate-limit per session (5/10min) → description required → image sniffed (PNG/JPEG/WEBP/GIF, size caps) → stored as note → surfaced in /reports/notes with status transitions and image endpoint.
files: agent/api.py, agent/reports.py
confidence: high

## APIS

Served (FastAPI, agent/api.py):
- POST /ask, POST /ask/debug, DELETE /session/{id}, GET /traces, GET /traces/{trace_id}, GET /stats, GET /dashboard (+named asset routes .css/.js/-app.js), POST /report, GET /reports/notes, GET /reports/notes/{id}/image, POST /reports/notes/{id}/status, GET /reports/voice, GET / (chat UI), plus WhatsApp webhook and GET /voice/chat/completions-style custom-LLM endpoint (ElevenLabs contract) [route names for whatsapp/voice inferred from module wiring].
Called (outbound):
- Gemini `generativelanguage.googleapis.com/v1beta/models/{model}:generateContent` (planner/answer/judge; defaults gemini-2.5-flash-lite, thinking low/minimal)
- Meta Graph `graph.facebook.com/v18.0` (send, mark_read, media)
- ElevenLabs (signed-url consumed by widgets; voicesync pushes config)
- Shamsieh admin API `{SHAMSIEH_API_BASE}/auth/login` + requests/uploads (institution_verify)
- S3 REST `https://{bucket}.s3.{region}.amazonaws.com` (hand-signed LIST/GET)

CLI: `python -m agent.cli` REPL; tools/*.py each have their own CLI surface (audits, cost, probes).

## DATABASE

Storage: PostgreSQL `shamsieh` (restored from production dumps; ~66 views are both the security boundary and semantic layer; role ai_reader read-only, 3s timeout); SQLite `traces/logbook.db` (turns, failures, judged verdicts, report notes); JSONL traces per day in traces/.
Entities: directory institutions (schools/universities/kindergartens/daycares/teachers/special-needs/housing/other) with fees/discounts/grades/gender policy/sections/location/contact; derived coverage denominators; enum vocabularies mirrored into catalog labels.yaml; logbook rows keyed by trace/session/channel/outcome with judged correctness strata.

## TESTS

Frameworks: bespoke zero-dependency runner (`tests/_runner.py`) executing every `test_*` function in plain assert-style files; node-based `tests/test_web.js` for markdown→HTML escaping (skipped with loud notice if node absent).
Commands: `make test` (29 python files + js); `make eval` (full golden run, concurrency 5), `make eval-fast` (categories security/impossible/entity_absent); audits run individually via `python tools/audit_*.py`.
Coverage style: 120+ deterministic checks across 13 files at last README count (now more files: claims, filters, robustness, security, vocab…); golden set 166 cases; boot-time gates re-verify enum vocabulary, coverage reachability, normalization parity, catalog consistency, and filter executability at every startup.

## GIT LESSONS

- c155647 (first commit, 2026-08-12) → 69 commits in ~2 weeks: extremely high iteration cadence with narrative commit messages that double as documentation ("A gate is a rule, not a row count" e66a028; "A measured zero is not a warning" 699008b).
- 8fc0317 `[loop] Set up the rollback net before touching anything`: loop rounds began by tagging stable-2026-08-13 (e056051) and freezing feature/full-coverage-multilingual — regression safety preceded change.
- d5694e4 "A routing test should not need a database": unit-level determinism kept tests fast and hermetic.
- dfba108 "Fix the blank dashboard: a module that parsed but did not evaluate": importable-but-inert modules shipped once; dashboards now evaluated, not just parsed.
- 5e053e6 "Discounts were never missing; the view read the wrong key": display-layer key mismatches masquerade as data gaps — audits materialize every view cell (tools/audit_views.py) because of this.
- 1dc16c3 "Audit for the whole class of honest-looking zeros, not one instance": recurring pattern — after each bug family appears, a class-hunting audit script follows.
- 2591d1d "Pick the model by measurement": model choice (gemini-3.5-flash-lite attempt, settled on 2.5-flash-lite) driven by measured p95 latency (3.97s) and quality, not vibes.
- b6b811f / feec45d / 698bb7c: review passes produced multi-defect fixes ("Four copy and direction defects the verdict pass found", "Apply the review's eight findings") — external review loops were institutionalized.
- 0e33135 "Keep both model names priced, and stop a duplicate key hiding a rate": pricing/config duplication caused silent metric loss.
- 0417f89 / 96ab050 / 2f28073: telephony-specific etiquette bugs (mid-call greetings, reading internal notes aloud, follow-ups answering about nothing) only surfaced via real conversations — the "[loop] Round N: five bugs that only a conversation could show" series (edd5e2e).

## DECISIONS

- Deterministic-first architecture: model calls reserved for planning prose and answer prose; everything else is code, YAML, or SQL.
- Security by construction: ai_reader + views + parameterized SQL + statement timeout + output number-guard + method-free design (no arbitrary tool execution).
- No AWS SDK: 40 lines of SigV4 hmac instead of boto3's 50MB dependency (refresh.py docstring).
- Named static asset routes instead of parameterized `/{asset}` (api.py comment documents the rejection).
- Rollback net + frozen stable branch + `[loop]` commit prefix as process technology.
- Country scoping defaults to global search rather than erroring when unknown.
- Tests fail loudly when infrastructure is missing (node notice) — "a security check that quietly stops running is worse than none".

## RISKS & TECH DEBT

- A 67 MB raw production dump (`production_backup_2026-08-09_03-00-02.sql`) sits in the working tree — convenient but a serious leak/mis-push hazard; `.env` with live tokens sits beside it (gitignored, but adjacent to committed work).
- Single-process FastAPI serves chat, WhatsApp, voice, dashboard, and admin endpoints together; no auth separation beyond ADMIN_API_KEY/VOICE_API_KEY headers on sensitive routes.
- LLM judge quality bounds the truthfulness metrics; Wilson intervals acknowledge but don't eliminate judge noise.
- Golden set and audits are strong but the fast-moving branch has outrun LOOP.md's stable-point numbers (157→166 cases) — docs lag code.
- SQLite logbook on the same host as the app is fine for one operator, but grows unbounded alongside daily JSONL traces.
- Hand-rolled SigV4 and hand-maintained allowlists/policy manifests depend on human discipline to stay in sync with counterparts elsewhere (cf. botify_agent addons in sibling repos mirroring SAFE_ACTION_METHODS).
- Voice/WhatsApp contracts pinned to specific provider API versions (WHATSAPP_API_VERSION default v18.0) — upgrade churn risk.

## UNCERTAIN

- Exact WhatsApp webhook path name (module wiring seen; route decorator not directly read).
- Whether the SHAMSIEH_API_BASE admin API is an internal Odoo (i.e., the shamsieh project's website_lead_api inverse) or a separate service [inferred separate service].
- Production host topology behind the public HTTPS front (tunnel vs reverse proxy unspecified in README's "للإنتاج" section).
- Relationship between catalog/domains counts (8 yaml files) and the "8 domains" router constant assumed consistent.
- gemini-3.5-flash-lite experiment (commit 2591d1d) vs current default gemini-2.5-flash-lite — which won in production config (.env not inspected beyond key names).
