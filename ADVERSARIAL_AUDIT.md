# Adversarial Retrieval Audit

Auditor: independent adversarial QA (read-only; no indexes or repos modified).
Date: 2026-08-25. CLI: `/home/aboud/project-cortex/bin/cortex` (doctor: all checks passed, 14 projects indexed).

Methodology: every claim below was checked against ground truth via `grep`/`ls`/`git` on the real repos. Emphasis on the failure classes a friendly demo hides.

## Scenario Results

| # | Scenario | Verdict | What happened |
|---|----------|---------|---------------|
| 1a | Cross-project: "How did we implement audit trails elsewhere?" | **PARTIAL** | Routed to mushagil only. Content found there is genuinely good (`audit_event`, UoW audit queue, RLS policy), but "elsewhere" was ignored — no survey of other projects, no acknowledgment that the question spans projects. |
| 1b | Cross-project: `search "WhatsApp integration"` | **FAIL** | Returned hits from exactly one project (mushagil), and none of them are WhatsApp code — top symbols are generic test harnesses (`IntegrationHarness`, `http-harness.ts`). Ground truth: WhatsApp code exists in **12 of 14 projects**; mawid-ai alone has 386 matching files (`packages/backend/src/whatsapp/*`). With `--project mawid-ai` the same query instantly returns its real whatsapp module — the index knows, the routing hides it. |
| 1c | Cross-project: "Which projects implement tenant isolation?" | **FAIL** | Question literally asks *which projects*; answer was a single-project briefing (mushagil). Ground truth: multi-tenant code concentrated in campify/chat-agent-saas/mushagil; zero in mawid-ai/sham-v2/umbrellaprime. No mechanism exists to answer the question asked. |
| 1d | `search "blueprint"` (no project) | **PARTIAL** | Correctly picked luma (the right project) but never mixes results across projects. Cross-project retrieval does not exist; there is only per-query single-project routing. |
| 2a | Vague: "fix the bug" | **FAIL** | Confidently selected "Next.js Web Application [verified]" module with primary files, from a task containing zero information. Implied claim "your bug lives here" is fabricated. |
| 2b | Vague: "it's broken" | **PASS** | Graceful refusal: "could not determine target project; pass project explicitly." (But exits 0.) |
| 2c | Vague: "make it faster" | **FAIL** | Same confident module briefing as 2a. No ambiguity gate before module selection. |
| 3a | Wrong-feature: "kubernetes deployment manifests" (no project) | **PASS** | Honest error instead of guessing. Ground truth: k8s manifests exist only in CVM (helm charts). |
| 3b | Wrong-feature: "modify the kubernetes manifests" --project campify | **PARTIAL** | Returned header + focus terms and nothing else — honest-empty (campify has zero deployment config), but never says "no Kubernetes in this project". Reads like a crash to a user. |
| 3c | Trap-inverted: "change the React component" --project cvm | **PASS** | CVM actually has a Next.js console; correct components returned (`apps/web/src/components/*`). Routing by keyword works when vocabulary exists. |
| 3d | Wrong-feature: "change the React component styling" --project iscc-testing | **PARTIAL** | Project is pure Python/Odoo (0 .tsx). Output honest-empty (no fabricated React files) but again no explicit "this project has no frontend / nearest concept" guardrail. |
| 4a | Nonexistent: "fix the GraphQL subscriptions in campify" | **PARTIAL** | No fabricated GraphQL files (good), but silently substituted the webhook-"subscriptions" module without flagging that GraphQL does not exist in the repo (0 graphql/apollo references). Near-miss presented as answer. |
| 4b | Nonexistent: "fix the blockchain module in luma" | **FAIL** | Confident garbage: full MODULE section ("shared PostgreSQL schema [inferred]") + primary files for a feature that has zero blockchain code behind it. |
| 4c | Nonexistent: "fix the blockchain smart contracts module" | **FAIL** | Fuzzy-matched "contracts" → "Generated API Contract & Client **[verified]**" module. The word `[verified]` attached to a hallucinated relevance judgment is worse than no answer. |
| 4d | Misrouted: "work on the blueprint sections feature" (luma vocabulary) | **FAIL** | Routed to mushagil, answered with "Background Worker Process [verified]" — completely unrelated. No low-confidence warning anywhere in output. |
| 5a | Arabic: "عدل نظام المصادقة" --project campify | **PASS** | Correctly surfaced auth files (apiKeyAuth.ts, auth migrations, authz contract tests). Arabic works when project given and vocabulary matches. |
| 5b | Arabic: "أضف حقل للحجوزات" (no project) | **PARTIAL** | Graceful "could not determine target project" — but bookings are core vocabulary in mushagil/mawid-ai; English equivalent likely routes. Exit code 0 on failure. |
| 5c | Arabic: same query --project mushagil | **FAIL** | Empty output (header + transliterated focus terms only) despite rich booking content. Yet `search "الحجوزات" --project mushagil` returns perfect booking hits (`booking_policy`, `BookingPolicyView`...). **Context-mode and search-mode have different matchers; context loses on Arabic where search wins.** |
| 5d | Arabic: "وين نعدل الحضور؟" --project mushagil | **PARTIAL** | Shows cross-lingual awareness ("الحضور" → translated "attendance" in focus terms) but surfaces zero modules/files. Translation happens, retrieval doesn't use it. |
| 6a | Impact sanity: campify `packages/core/src/webhooks/dispatch.ts` | **FAIL** | Claimed "RISK: LOW (isolated)", listed zero callers/tests. Ground truth: production caller `apps/worker/src/main.ts:140` calls `dispatchWebhookDelivery`; integration test `apps/worker/test/webhookPipeline.integration.test.ts` exercises it. False negative on both callers AND tests. Dangerous for refactor-risk assessment. |
| 6b | Impact sanity: mushagil `unit-of-work.ts` | **PARTIAL** | Cited test file is real and on-topic (`unit-of-work-atomicity.test.ts`, verified). But omitted all real importers: `pg-transaction-runner.ts`, `postgres-idempotency-store.ts`, `processed-event-guard.ts`, platform barrel. Caller graph systematically incomplete. |
| 6c | Impact sanity: luma `auth.routes.js` | **PASS** | Genuinely good: importer `routes.loader.js:5` correct, all 8 API routes accurate (grep confirms 8 `router.post`), test file exists with 98 topic matches. Impact quality varies wildly per project — luma's index is the outlier, not the norm. |
| 7a | Freshness: Telvora (237 dirty files per `git status --porcelain`) | **FAIL** | Context header says "FRESHNESS: fresh"; `cortex status --project telvora` says "Freshness: FRESH ... Memories: 21 (0 stale)". Freshness = index↔HEAD commit only; working-tree divergence is invisible. An agent told FRESH will assume disk matches the last commit. |
| 7b | Freshness: stale knowledge served as fact (mushagil) | **FAIL** | Mushagil's pitfall memory states "~136 dirty files / M03 uncommitted [pitfall|verified]". Reality: M03 committed at `49518ad`, tree clean. Stale snapshot served as verified current-state with no staleness flag — actively misleading in the opposite direction too. |
| 8a | Budget: same task at --budget 800 vs 8000 (campify rate limiting) | **PASS** | Coherent degradation: budget 800 keeps HEADER/PRIMARY FILES/READ FIRST/LIKELY IMPACT/TESTS/API SURFACE/HISTORY; drops KNOWLEDGE/PITFALLS/DEPENDENCIES/MODULE first. Top-ranked file at both budgets is `apps/api/src/rateLimit.ts` — the actual file. This is the best-behaved feature tested. |
| 8b | Misc: `cortex tests <nonexistent path>` | **PARTIAL** | Silently returns an unrelated test file (`failure.unit.test.ts`) for a path that doesn't exist. Fuzzy fallback without "not found". |

**Tally: 7 PASS · 9 PARTIAL · 9 FAIL**

## Failure Analysis

1. **Cross-project retrieval does not exist.** Every query is routed to exactly one project (keyword-overlap router; unanchored queries fall back to mushagil). Search results carry a project column, so the data model already supports federation — there is simply no merge/fan-out path. Any "where did we do X elsewhere?" question is structurally unanswerable, and the system doesn't say so; it answers a different, narrower question silently.

2. **No existence guardrail → confident garbage.** When task vocabulary has no lexical anchor in the chosen project (blockchain, blueprint-sections-in-mushagil), the fuzzy matcher grabs surface-similar tokens ("contracts" → API contracts) and emits a full MODULE briefing tagged `[verified]`. There is no threshold check of "did any focus term actually hit?" before composing the answer. The `verified/inferred` labels describe *provenance of the module doc*, not *confidence that the module answers the task* — conflating these makes the label system lie.

3. **Two different retrievers.** Search-mode matched Arabic token "الحجوزات" to booking symbols perfectly; context-mode returned empty for the same concept in the same project. Whatever matcher/context uses (different tokenizer? stricter threshold?) is strictly weaker for non-Latin scripts. Partial evidence of Arabic handling (transliteration in focus terms) shows intent without follow-through.

4. **Impact graph has holes precisely where it matters.** Luma (Express, direct `require` in one loader file) gets perfect impact; campify misses a production caller through the barrel re-export path (`core/src/index.ts` → worker import), and mushagil lists tests but zero of four importers. Likely cause: import-edge extraction skips barrel re-exports and/or cross-package imports. False-negative risk assessments are the most dangerous output a refactor-assistant can produce.

5. **Freshness means "index vs HEAD", nothing more.** Working-tree state (237 dirty files in Telvora) is never consulted at query time, and stored knowledge memories are never re-validated against current git state — so the system simultaneously under-reports dirtiness (Telvora) and over-reports staleness as current fact (mushagil M03). The "(0 stale)" counter is computed against the wrong clock.

6. **No ambiguity gate.** Zero-information tasks ("fix the bug") pass straight into module selection and receive the same confident formatting as specific ones. The router *can* detect hopeless queries ("it's broken") but only at the project-selection stage, not the content stage.

7. **CLI hygiene:** failures exit 0 ("could not determine target project", empty outputs), which hides breakage from any scripted/agent caller.

## Top Fixes Recommended

Ranked by risk-retired-per-effort:

1. **Existence guardrail before composition (kills the worst FAIL class).** In `context`: if fewer than N focus terms hit any symbol/file/memory above a minimal score, return `"no confident match for '<task>' in <project>; nearest concepts: …"` instead of a module briefing. Never attach `[verified]` to an answer whose task-term overlap is ~zero. Cheap, mechanical, converts FAILs 2a/2c/4b/4c/4d into honest PARTIAL/PASS.
2. **Federate search/context across projects when the query demands it.** Trigger fan-out on interrogative patterns ("where/which/elsewhere/across/before") or an explicit `--all` flag; merge existing per-project result sets (already produced internally) and rank. The index needs no changes — only a merge layer. Converts 1a–1d from structural impossibility to a real capability.
3. **Fix import-edge extraction through barrels/re-exports**, then re-index campify/mushagil. Verify `dispatch.ts ← apps/worker/src/main.ts` appears after fix. Impact false negatives directly cause broken refactors.
4. **Working-tree freshness check at query time**: cheap cached `git status --porcelain | wc -l` per project; append `dirty=N` to the FRESHNESS line and warn when N > 0. Re-validate stored pitfall/current-state memories against HEAD at access time (or timestamp-stale them). Fixes 7a/7b in both directions.
5. **Ambiguity gate**: if the task has < 2–3 content words after stopwords, ask what to fix rather than picking a module. One regex-level check upstream of module selection.
6. **Unify context-mode retrieval with search-mode's matcher** (or lower its threshold for non-Latin tokens). Search already proves Arabic recall works; this is deletion of an inferior duplicate path, not new engineering.
7. **Exit non-zero on all failure paths** ("could not determine target project", empty context output, not-found paths in `tests`) so agent/scripted callers can detect failure.
8. **Explicit "not applicable" messaging for wrong-paradigm tasks** (kubernetes in a repo with no deploy config, React in Odoo): name the miss and offer the nearest real concept instead of returning a silent empty shell.

Bottom line: the per-project machinery (memory, modules, budgeting, luma-style impact) is genuinely strong, and the system fails honestly more often than systems of this type usually do. But it currently *fabricates relevance confidence* on out-of-vocabulary tasks, cannot see across its own projects, and reports freshness it does not measure. Until fixes 1–4 land, treat every context output as unverified when the task names a feature you haven't confirmed exists in the routed project.
