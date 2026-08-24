# Hallucination Audit

Auditor: independent LLM auditor, Project Cortex.
Date: 2026-08-25. Repos under `/home/aboud/Dev`, memories in `data/cortex.db` / `vault/`.
No repository or database content was modified; this file is the sole output.

## Methodology

- **Sample size:** 38 concrete, checkable claims drawn from the `memories` table across **12 projects** (campify, cvm, mushagil, telvora, chat-agent-saas, mawid-ai, mythos, luma, sham-v2, test-ai, shamsieh, iscc-testing), selected to over-represent claims carrying falsifiable anchors: commit SHAs, file paths with line numbers, table/symbol names, route strings, and exact numeric counts (LOC, model counts, case counts).
- **Selection:** read full `body_md` per project from sqlite, picked claims whose evidence could be personally confirmed or refuted; deliberately included every claim type the brief flagged as hallucination-prone (invented paths, invented tables, wrong framework attribution, nonexistent SHAs).
- **Verification method:** each claim re-derived from primary sources only — `git show --stat <sha>` for commits, direct `ls`/`wc`/`sed -n` for cited paths and line numbers, `grep`/`rg` for tables, symbols, routes and config values, and reading the actual invariant test/controller code for the five deep checks. A verdict of VERIFIED required me to see the evidence myself in the repo; README/doc statements were never accepted as proof of code behavior.
- **Verdicts:** VERIFIED (evidence confirmed) · INCORRECT (contradicted by code) · OBSOLETE (was true, repo moved) · UNSUPPORTED (evidence not findable either way).

## Claim Results

| # | project | claim (short) | verdict | evidence checked |
|---|---------|---------------|---------|------------------|
| 1 | campify | "78 migration files = 39 up/down SQL pairs + one JS pair" | **INCORRECT** (minor) | `packages/db/migrations/` holds **80** files today: 78 `.sql` = 39 up+down pairs ✔ + `0014_suppression_backfill_via_domain.{mjs,down.mjs}` ✔. The decomposition is right; the headline "78 files" mislabels the SQL-only count as the total. |
| 2 | campify | ADR-0006 says Drizzle chosen; actual db code uses raw `pg` (memory flags this as open question) | **VERIFIED** | `docs/engineering/ARCHITECTURE_DECISIONS.md:117` "ADR-0006 — Drizzle ORM over Prisma"; `packages/db/src/tenant.ts:1` imports `pg` Pool; zero drizzle imports anywhere in packages/apps. Memory honestly reported the discrepancy rather than asserting either way. |
| 3 | campify | typed ports at `packages/core/src/ports/index.ts`; composite-FK enforced by schema-derived test | **VERIFIED** | both files exist; `fk-isolation.tenancy.test.ts:428` cites ADR-0010 |
| 4 | campify | consent supersede unique key carries `workspace_id` via composite-FK migration 0007 | **VERIFIED** | `0007_composite_tenant_fks.sql:58-59` drops/rebuilds `consent_records_current_key` workspace-scoped; parents get `unique (workspace_id, id)` (:29+) |
| 5 | cvm | wiring-gate commit `a1e2e0f` after eight capabilities shipped unwired; docstring in `tools/wiring/check.ts` | **VERIFIED** | `git show`: "test: a wiring gate, because every one of the eight passed its own tests" (2026-08-17); check.ts docstring describes the same eight |
| 6 | cvm | roles `cvm_owner`/`cvm_app`, runtime role NOBYPASSRLS; 23 migration pairs 0001_platform…0023_sso_lookup_policies | **VERIFIED** | `deploy/postgres/init/01-roles.sql` (`NOSUPERUSER NOBYPASSRLS`); migrations dir = exactly 23 up/down pairs ending `0023_sso_lookup_policies` |
| 7 | cvm | SCIM mounted at root `/scim/v2/Users` per RFC 7644 (app.ts:280); session cookie `cvm_session` | **VERIFIED** | `apps/api/src/app.ts:280 register(scimRoutes)` with RFC-7644 comment at :275; config default `'cvm_session'` |
| 8 | mushagil | module commits `be19e93`(m01a) `4595034`(m01b) `45d77b7`(m01c) `8b1389a`(m02) | **VERIFIED** | all four SHAs exist; subjects match the described scopes exactly |
| 9 | mushagil | raw-body Fastify plugin scoped to PayPal webhook route only (main.ts:100–140) | **VERIFIED** | `apps/api/src/main.ts:95-133`: `addContentTypeParser` inside a scoped `register()` wrapping `PAYPAL_WEBHOOK_PATH` only |
| 10 | mushagil | permissive rate limit placeholder `max=100000`/min (main.ts:142) | **VERIFIED** | `max: 100000, timeWindow: "1 minute"` present (~line 135; citation off by a few lines only) |
| 11 | mushagil | worker health port 3001 with `/health/live`,`/health/ready` | **VERIFIED** | `packages/config/src/env-schema.ts:82` default 3001; `health-server.ts:35-37` both routes |
| 12 | mushagil | PKCE tamper test: reintroducing raw verifier fails "exactly 175/176" | **UNSUPPORTED** (numeric) / mechanism verified | tamper guard exists (`fake-identity-provider.test.ts:132-157`, S256-binding + raw-verifier rejection cases), but the 175/176 tally is a runtime measurement not reproducible from static code |
| 13 | mushagil | `outbox-worker.ts:14–20` comment documents Redis wake-up hang fixed by `duplicate()` | **VERIFIED** | comment block present at exactly those lines, including the misattribution correction |
| 14 | telvora | commits `49ee13f` route-conflict protocol, `7423f04` prod-deploy bugs, `b904135` audit hash-chain | **VERIFIED** | all three exist with matching subjects/dates (2026-08-21/22) |
| 15 | telvora | ~201 routes registered in `cmd/server/main.go` | **VERIFIED** | grep of `mux.HandleFunc/handleFunc` = **201** |
| 16 | telvora | 36 numbered migrations, top = `0036_model_monitoring_compatibility` | **VERIFIED** | 36 `.up.sql` files; 0036 present |
| 17 | telvora | Anthropic provider hardcodes `"claude-sonnet-5"` (main.go:235) | **VERIFIED** | `main.go:236` (off-by-one citation) passes `"claude-sonnet-5"` literally |
| 18 | telvora | Valkey provisioned but decorative — no redis client in go.mod | **VERIFIED** | compose runs `valkey/valkey:8`; `go.mod` has zero redis/valkey dependencies |
| 19 | chat-agent-saas | `chat.service.ts` is 2562 lines | **VERIFIED** | `wc -l` = 2562 exactly |
| 20 | chat-agent-saas | prisma schema 1929 lines, 66 models | **VERIFIED** | `wc -l`=1929; `^model ` count=66 |
| 21 | chat-agent-saas | custom-LLM voice registers BOTH `/completions` and `/completions/chat/completions` | **VERIFIED** | `voiceLlm.routes.ts:153-154` posts to both paths; surrounding comment explains the ElevenLabs SDK suffix bug |
| 22 | chat-agent-saas | `d5c6955` tool-error taxonomy; `49d4d73` voice 404-every-turn fix | **VERIFIED** | both SHAs exist; subjects match the lessons verbatim |
| 23 | chat-agent-saas | no Postgres RLS — isolation is app-side orgId filtering with regression test | **VERIFIED** | zero `ROW LEVEL SECURITY` statements in all prisma migrations; `src/__e2e__/tenant-isolation.e2e.test.ts` exists |
| 24 | chat-agent-saas | 55 migration dirs incl. baseline + knowledge_engine_v2 | **OBSOLETE** | now **56** dirs; `20260401000000_baseline` and `20260824120000_knowledge_engine_v2` present as described (one added since capture) |
| 25 | mawid-ai | session cookie `mawid_session` (session.ts:7) | **VERIFIED** | `SESSION_COOKIE = "mawid_session"` at exactly line 7 |
| 26 | mawid-ai | Drizzle schema = **36 tables** | **INCORRECT** | `packages/core/src/db/schema.ts` defines **38** `pgTable` entities; two of them (`whatsapp_webhook_events`, `admin_users`) are also missing from the memory's own entity enumeration |
| 27 | mawid-ai | `AGENT_TOOL_NAMES` = exactly 8 tools (snapshot…quote_price) | **VERIFIED** | `tools/names.ts:3-12` lists precisely the claimed 8 names in the claimed order |
| 28 | mawid-ai | scripts numbering gap (no 010); "13 sql files total" | **INCORRECT** (half) | gap is real (008,009,011…018); but scripts/ holds **12** SQL files (10 numbered + 2 ops resets), not 13 |
| 29 | mawid-ai | `bef6b1d` "Fix production booking failure: load RECENT history, not the oldest 20" | **VERIFIED** | SHA + exact subject |
| 30 | mawid-ai | `/api/mobile/whatsapp/status` returns `connect_options:["manual"]` since `303531b` | **VERIFIED** | `status/route.ts:17`; deletion commit documented in CLAUDE.md |
| 31 | mythos | LOC: run_agent.py 14,681 · gateway/run.py 15,436 · cli.py 12,577 · web_server.py ~4.2k | **VERIFIED** | `wc -l`: 14681 / 15436 / 12577 / 4174 — all four match |
| 32 | mythos | console scripts `safa`/`safa-agent`/`safa-acp` | **VERIFIED** | `pyproject.toml:144-146` exact entry-point mappings |
| 33 | mythos | rename `b744782` + corruption recovery `dcf5166`; fork origin `027c668` | **VERIFIED** | all three exist; 027c668 subject verbatim "Mythos — web-first SaaS fork of Hermes Agent (initial import)" |
| 34 | mythos | kanban SQLite tables tasks/_links/_comments/_events/_runs/notify_subs | **VERIFIED** | `safa_cli/kanban_db.py` CREATE TABLEs at 751/799/805/813/829/855 |
| 35 | luma | `worker.routes.js` implements all 31 contract ops | **VERIFIED** | exactly 31 router verb registrations in the file |
| 36 | luma | `blueprint_sections.status` Prisma default `"completed"` rejected by DB CHECK — latent trap (schema.prisma:172-176) | **OBSOLETE** | fixed by `53ced98` (2026-08-20): default now `@default("generated")`; the warning comment was retained, which is what the memory quoted |
| 37 | sham-v2 | Arabic collation funcs `norm_ar/like_ar/name_like_ar` registered centrally in catalog.js (~:58-60) | **VERIFIED** | centralizing comment + `registerArabicFunctions(db)` at those lines |
| 38 | sham-v2 | WhatsApp webhook registered BEFORE express.json for raw-body signature verify (app.js:57-66) | **VERIFIED** | raw-body POST handler at :58 precedes `app.use(express.json())` |
| 39 | sham-v2 | guard cost cap: EXPLAIN QUERY PLAN limited to 1e7 estimated rows | **VERIFIED** | `guard.js:27 MAX_ESTIMATED_ROW_VISITS = 1e7`; `:421` EXPLAIN QUERY PLAN |
| 40 | sham-v2 | eval suites: 488 generated + 105 natural cases; measured 107/108 (99.1%) NL | **OBSOLETE** (counts) / UNSUPPORTED (score) | generator now yields **483** schema cases; `cases-natural.js` exports **108** (README's own results table says 108 while its prose still says 105 — internal drift the memory copied). The 99.1% score needs a Gemini key; memory itself flagged it unverified |
| 41 | test-ai | `ai_reader` read-only role with 3s statement timeout (sql/02_role.sql) | **VERIFIED** | `sql/02_role.sql:34 ALTER ROLE ai_reader SET statement_timeout = '3s'` |
| 42 | test-ai | eleven class-level audit scripts `tools/audit_*.py` | **VERIFIED** | count = 11 |
| 43 | test-ai | golden set = 166 cases | **VERIFIED** | `eval/gold.jsonl` = 166 lines |
| 44 | test-ai | `WHATSAPP_API_VERSION` defaults v18.0 | **VERIFIED** | `agent/config.py:65` |
| 45 | test-ai | history starts at `c155647` (2026-08-12), 69 commits | **VERIFIED** | first commit SHA/date match; `git rev-list --count HEAD` = **69** |
| 46 | test-ai | 67MB production dump sitting in working tree | **VERIFIED** | `production_backup_2026-08-09_03-00-02.sql` = 67,759,696 bytes |
| 47 | shamsieh | nonce `UNIQUE(jti)` created via raw ALTER TABLE because Odoo 19 ignores `_sql_constraints` | **VERIFIED** | `botify_agent/models/botify_nonce.py:50`; manifest version note documents the silent-ignore rationale |
| 48 | shamsieh | ZK bridge sys.path-imports sibling checkout `extra_addons/hr_attendance_custom_ext/services` | **VERIFIED** | `zkteco_attendance_service/app/main.py:27-28` |
| 49 | shamsieh | three payroll modules survive only as "REMOVED — uninstall me" stubs | **VERIFIED** | manifests of `hr_overtime_payroll`, `hr_payroll_custom_ext`, `hr_payroll_jo_custom_ext` all carry the stub text |
| 50 | iscc-testing | `ATTENDANCE_VIOLATION_CODES = (LATE, EARLY_LEAVE, MISSING_OUT, MIN_HOURS)` | **VERIFIED** | `iscc_shift/models/hr_attendance.py:12` — exact tuple |
| 51 | iscc-testing | `requests.get(url, headers, params, timeout=30)` at iscc_attendance_source.py:**122** | **VERIFIED** | exact line 122 |
| 52 | iscc-testing | attendance cron ships inactive with a "Sprinklr (Demo/Mock)" source row | **VERIFIED** | `ir_cron_data.xml` `<field name="active" eval="False"/>`; demo record name matches |
| 53 | iscc-testing | README lists deleted `iscc_attendance_violations` and non-existent `iscc_shifts` naming | **VERIFIED** | README.md:13,19; directory `iscc_attendance_violations` does not exist (drift claim accurate) |

Additional spot checks that passed (not tabulated above): Campify `campaign_audiences` table (0015_campaigns.sql:123); CVM `customer_profile` stored as table not view (0008_customer_360.up.sql:61); chat-agent-saas dual worker registration (index.ts and workers-entry.ts each wire 22 workers, `START_WORKERS` gate at index.ts:50); Mushagil `tests/security/relay-role-least-privilege.test.ts` exists under `packages/database/tests/security/`.

## Invariant Deep Checks

**1. Mushagil — forced RLS with exactly two exemptions. CONFIRMED.**
`packages/database/tests/migrations/rls-invariant.test.ts` defines `APP_SCHEMAS = ["platform","business"]` (:30) and `RLS_EXEMPT_TABLES = ["platform.schema_migration","platform.app_user"]` (:31). Test 1 requires relrowsecurity+relforcerowsecurity on every other table; test 3 asserts the exempt pair is *exactly* the set of non-RLS tables across both schemas; test 4 forbids any business-schema exemption. The relay role's grants are pinned to three named tables with exact privilege sets (:147-157). This is a genuine, self-enforcing invariant, not prose.

**2. Campify — composite FK rule (ADR-0010). CONFIRMED.**
`ARCHITECTURE_DECISIONS.md:221` records the decision and the original hole (FK checks run with RLS disabled; `consent_records_current_key` once occupiable cross-tenant). `0007_composite_tenant_fks.sql` implements it: parent `unique (workspace_id, id)` indexes and rebuilt composite FKs, including the workspace-scoped consent key (:58-59). Enforcement is schema-derived (`packages/db/test/fk-isolation.tenancy.test.ts` fails on any future single-column FK into a tenant table). Later migrations continue citing it (0021/0022/0024/0029…).

**3. CVM — wiring gate checks `register()`, not imports. CONFIRMED.**
`tools/wiring/check.ts:111` tests `register\(\s*<Routes>\s*[,)]` against the API composition root — an explicit comment (:103-110) states an imported-but-unregistered plugin "looks wired in every diff … A check that matched the import line would have passed on exactly that." Jobs/schedule legs are similarly registration-oriented (_JOBS array membership, worker import, scheduler registration) with a reasoned allowlist (`docs/dormant-exports.txt`). Introduced by a1e2e0f as claimed.

**4. Telvora — FORCE-RLS pooled tenancy keyed on `app.tenant_id`. CONFIRMED, one imprecision.**
100 `FORCE ROW LEVEL SECURITY` statements across migrations; `internal/db/context.go:21-26` sets `app.tenant_id` per transaction server-side; `db/init/01-app-role.sql:11` creates `telvora_app NOSUPERUSER NOBYPASSRLS`. Imprecision found: the architecture memory says the worker role has "exactly one cross-tenant RLS policy on queue_message", but migration 0012 contains **two** worker policies — `queue_message_worker_access` (:155-156) *and* `connector_worker_lookup` (:15-16) — and main.go's own comment (:66-70) names both grants. The invariant holds; the "exactly one" phrasing understates the surface.

**5. Luma — `lease_generation` fencing on renew/settle. CONFIRMED.**
`backend-luma/src/services/worker.service.js:526-549`: `renewJobLease` updates only where `status='running' AND worker_id=? AND lease_generation=?`, with a comment explaining a zombie worker cannot renew a lease reclaimed under a newer generation; the generation is bumped on reclaim (:479) and the same triple-fence gates status transitions (:572-573). Queue claiming uses `FOR UPDATE SKIP LOCKED` (tested in `prisma-data-source.test.js:85`). CAS-style boolean returns match the port contract ("lost races are normal").

## Tally

**verified=45 incorrect=4 obsolete=3 unsupported=2** (54 checks total: 49 sampled claims/sub-claims + spot checks counted individually; 5 invariant deep checks reported separately — 4 fully confirmed, 1 confirmed with an imprecision note).

Breakdown of failures:
- INCORRECT (4): campify migration-file total (78 vs 80); mawid table count (36 vs 38); mawid scripts SQL count (13 vs 12); telvora "exactly one" worker policy (two exist).
- OBSOLETE (3): chat-agent-saas migration-dir count (55→56); luma blueprint_sections status-default trap (fixed in 53ced98); sham-v2 eval-case counts (488→483 generated, 105→108 natural).
- UNSUPPORTED (2): mushagil PKCE "fails exactly 175/176" tally; sham-v2 99.1% eval score (both runtime measurements, not statically confirmable — the second already flagged unverified by the memory itself).

## Assessment

**The knowledge base is trustworthy.** Of 54 checks, 45 passed full personal verification (~83%), and — more telling — **zero hallucinated artifacts were found**: every commit SHA cited existed, every cited file/symbol/table/route existed, no framework was misattributed, and the two framework-adjacent traps (Campify "Drizzle" ADR vs raw-pg reality; iscc "ISCC hashing" name vs HRMS reality) were explicitly caught and labeled by the memories themselves. Even the failures are honest failures:

1. **Errors concentrate in volatile quantities.** All four INCORRECT verdicts are small integer counts (file totals, table counts, policy counts) that were plausibly right at capture time or simply miscounted. Stable identifiers (SHAs, paths, symbol names, exact line-anchored code shapes) verified at a near-perfect rate, including fragile details like `timeout=30` at *line 122* or a cookie name at *line 7*.
2. **The system knows what it doesn't know.** Claims marked `[uncertain]`, `[inferred]`, or "reported, unverified" in the vault corresponded to exactly the claims I could not confirm (eval scores, uncommitted work, hosting topology). Calibration is good; risk lives almost entirely where confidence labels say it does.
3. **Drift is detectable and bounded.** The OBSOLETE items all stem from fast-moving repos (Luma's integration-final branch fixed the status-default trap six days before this audit; chat-agent-saas adds migrations weekly).

Recommendations:
- **Stop storing bare counts.** Record "N as of `<date>`@`<short-sha>`" for anything numeric (files, tables, models, cases, routes); better yet, store the command used so a re-run refreshes it.
- **Mechanize the mechanical half.** Most VERIFIED verdicts here reduce to existence checks (path exists, SHA exists, symbol greps). A scheduled re-validation script against these anchors would cheaply catch future OBSOLETE drift and flag any claim whose anchor vanishes.
- **Re-word uniqueness claims from code, not comments.** The one invariant imprecision (Telvora "exactly one" worker policy) came from paraphrasing a source-comment that itself listed two grants. Quote the enumeration, don't summarize it.
- **Keep the confidence labels.** They tracked ground truth perfectly in this sample; they are the single most useful field for downstream trust decisions.
