# CORTEX REPORT — chat-agent-saas

## META
project_id: chat-agent-saas
root: /home/aboud/Dev/chat-agent-saas
kind: multi-tenant SaaS monorepo (embeddable AI chat + voice agents, product name "Botify", botifyarabia.ai)
languages: TypeScript (~850 ts/tsx), Python (Odoo addon), SQL (Prisma migrations), shell (deploy scripts)
frameworks: Express 4 + Socket.IO 4 (API), Next.js 16 App Router + React 19 (web, platform-admin), Vite vanilla TS (widget), Prisma 6 + PostgreSQL/pgvector 16, BullMQ + Redis, LangChain 1.x (@langchain/google-genai|openai|anthropic|mcp-adapters), Zod, Pino, Sentry, Tailwind, next-intl + react-i18next, ElevenLabs SDK (@elevenlabs/client, @elevenlabs/react)
package_managers: npm workspaces + Turorepo 2 (NOT pnpm despite task brief; verified: root package.json `packageManager: npm@10.8.0`, package-lock.json present, workspaces packages/*)
test_frameworks: Vitest 4 (two tiers: infra-free `*.test.ts`, DB-bound `*.e2e.test.ts` via vitest.e2e.config.ts), Supertest for HTTP e2e
deployment: single EC2 box, PM2 (ecosystem.config.cjs: chatagent-api / chatagent-workers / chatagent-web / chatagent-admin) behind nginx (infra/nginx/), manual rsync deploy.sh with migration-guard + pg_dump snapshot + /api/ready health gate, GitHub Actions CI (.github/workflows/ci.yml quality+docker jobs, deploy-staging.yml). Local infra via docker-compose (pgvector, Redis 7, MinIO).
git_state: branch `deploy/voice-custom-llm-2026-08-19`, 144 dirty files (83 modified, 61 untracked) — large in-flight "integration engine v2" refactor; master is the generic product baseline.

## OVERVIEW
chat-agent-saas ("Botify") is a multi-tenant Arabic/English SaaS for building embeddable AI agents: per-tenant RAG knowledge bases, tool-calling against customer systems (Odoo ERP, Dynatrace, Splunk, generic MCP servers, custom HTTP actions), live human handoff, outbound campaigns/journeys/push/social, conversation analytics, and voice calls through ElevenLabs Conversational AI. The tenant surface is a Next.js dashboard; marketing is server-rendered ar/en for SEO; an embeddable dependency-light widget ships as IIFE bundles. Verified from CLAUDE.md, packages/*/package.json, and source.

The backend (`packages/api`, Express) is the bulk of the system: ~24 feature modules under `src/modules/`, cross-cutting services under `src/services/` (AI provider routing, RAG over pgvector, memory layers, safety screening, integrations, identity, realtime), and ~24 BullMQ workers split into their own production process tier (`src/workers-entry.ts`, `START_WORKERS=false`). Multi-tenancy is Organization-rooted with orgId filtering in every service query plus RBAC string permissions; isolation is regression-tested in `src/__e2e__/tenant-isolation.e2e.test.ts`. Billing is custom (Subscription limits per rolling period, Plan/FeatureCatalog), no Stripe [verified via schema models].

The current deploy branch carries two big workstreams visible in git log + untracked files: (1) the ElevenLabs **custom-LLM voice bridge** — our own OpenAI-compatible endpoint `/api/voice-llm/:agentId/completions` replaces ElevenLabs' native LLM so voice reuses the exact text-chat brain (RAG, tools, safety) in one round trip per turn [services/elevenlabs/voiceLlm.routes.ts]; (2) an **integration-engine hardening wave** (untracked capabilityRegistry/accessPolicy/evidence/evaluationSuites services, dynatraceErrors/odooErrors, knowledge engine v2 chunker/reranker, ReportArtifact model + migrations) that implements the findings of `docs/integrations/architecture-audit-2026-08-24.md`. A separate Odoo addon (`integrations/odoo/botify_agent`, Python) runs inside customer Odoo instances for signed end-user identity and record-rule enforcement.

A historical side product "Campify" (standalone campaign-manager Next.js app, ~70 commits) was merged then fully removed from master and rebuilt as the `outreach` module inside the API (see GIT LESSONS).

## ARCHITECTURE
- Monorepo graph (turbo.json): build/lint/test depend on `^build`; `@chatagent/shared` must be built before consumers (exports map src-for-import/dist-for-require). globalPassThroughEnv whitelists DATABASE_URL/REDIS_URL/ENCRYPTION_KEY/JWT_SECRET/JWT_REFRESH_SECRET/GOOGLE_AI_API_KEY/GEMINI_API_KEY — new runtime env vars must be added there or CI tasks can't see them.
- API process tiers: same worker set registered from TWO files — `packages/api/src/index.ts` (in-process when START_WORKERS!=='false') and `src/workers-entry.ts` (prod tier). Prod runs api with START_WORKERS=false + separate workers process (ecosystem.config.cjs). A worker registered in only one file silently never runs in one environment. Both files side-effect-import `./services/integrations/providers` to populate the provider registry.
- Boot order (index.ts, 95 lines): load-env → initSentry → validateEnvSecrets → preloadConfigs (DB SystemConfig cache, hot-reload via Redis pub/sub, utils/config.ts) → createApp → listen :3000 → start workers.
- App middleware chain (app.ts:141-357): trust proxy → Socket.IO with @socket.io/redis-adapter stored on app.set('io') → helmet/compression/CORS/cookies/json(10mb) → requestLogger → metrics → rateLimiter (Redis-backed, 800/15min default, off in dev) → routes → errorHandler. Route mounting order matters: outreach sub-routers mount BEFORE catch-all `/api/outreach`; knowledge/analytics/integrations/actions all mount under `/api/agents`.
- Chat hot path: modules/chat/chat.service.ts (2562 lines) — public POST → agent-origin validation → resolveWorkspaceAi (agent override → org default → platform default) → RAG retrieval (pgvector, parallel) + tool loaders (MCP/Odoo/Dynatrace/Splunk/custom actions/files) → bounded runToolLoop (10 iters text / 6 voice, per-call timeouts) → createStreamMarkerFilter strips `[ESCALATE_TO_HUMAN]`/(DOC n) markers across token boundaries → persist Conversation/Message → Socket.IO emit → async analysis job.
- AI layer (services/ai/): modelProvider.ts routes gemini/openai/anthropic with per-provider model validation + SystemConfig key fallback; embeddings.ts (gemini-embedding-001, dim 1536); rag.ts pgvector HNSW cosine on DocumentChunk; memory.ts (20-msg/12k-char window + rolling summary + durable per-customer facts only for verified identity); safetyScreening.ts lexicon+optional classifier; geminiToolSchema.ts sanitizes schemas for Gemini's strict validator; customActions.ts risk-tiered confirmation gate for high-risk HTTP actions.
- Voice pipeline (services/elevenlabs/, the deploy-branch focus): three coexisting paths — (a) legacy native-LLM + webhook tool (voiceTools.ts, whole-pipeline-as-one-tool), (b) custom-LLM bridge voiceLlm.routes.ts mounted at `/api/voice-llm` (OpenAI-SSE contract; agent.config.compliance.voice.customLlm===true gate; X-API-Key shared secret; X-App-Conversation-Id dynamic-variable correlation; identity re-derived from conv.identitySessionId per turn), (c) native MCP server mcpServer.routes.ts at `/api/mcp/elevenlabs` exposing discrete tools (check_availability/book_appointment/request_human_agent). agentConfigSync.ts pushes config to ElevenLabs incl. custom_llm.url; widget voice-loader lazy-injects widget-voice.iife.js (ElevenLabs SDK) on first voice call.
- Background jobs (jobs/queue.ts): 13 queues (knowledge-processing, knowledge-sync, conversation-analysis, integration-token-refresh, integration-poll, 5×outreach, journey-tick, social-publish, social-metrics); finite retries/backoff/TTL defaults; repeatable sweeps (journey tick 60s, social scan 60s, metrics 6h); token refresh uses delayed jobs with deterministic jobIds; analysis job delays 3s post-close with fixed 70s backoff tuned to Gemini 429s.
- External integrations: Odoo (JSON-RPC + signed addon, deny-by-default policy manifest, enterprise ledger/delegation/approvals), Dynatrace (Classic v2 APIs + Grail/DQL fallback, scope-gated tools, SSRF guards), Splunk (MCP client, SPL guard, circuit breaker), Meta/WhatsApp/X/LinkedIn channels, Resend/SMTP email, web-push VAPID, MinIO/S3 storage with AES-signed private URLs.
- Frontends: web = two root layouts by route group — `(marketing)/[locale]` next-intl SSR SEO surface, `(app)/[locale]` dark-only dashboard (robots noindex); platform-admin = noindex console on :5174; both are Node servers in prod (next start behind nginx, NOT output:'standalone' — see DECISIONS).

## MODULES
### api-chat — Chat pipeline & agent runtime
purpose: public + authenticated chat endpoints, the tool loop, streaming, quotas, handoff, safety screening.
path_prefixes: packages/api/src/modules/chat/, packages/api/src/services/ai/
key_files: modules/chat/chat.service.ts (2562 ln), chat.controller.ts, streamMarkerFilter.ts (+test), runToolLoop.usage.test.ts, services/ai/{modelProvider,geminiToolSchema,safetyScreening,memory,rag,resolveWorkspaceAi}.ts
entrypoints: POST /api/chat/* (public widget path, origin-checked); processMessage/processMessageStream/processPlaygroundMessage exports reused by playground and voiceLlm route.
responsibilities: conversation ownership, quota checks (assertMessageQuota/assertVoiceQuota), resource loading (RAG topK + MCP/custom-action/file/Odoo/Dynatrace/Splunk bundles), bounded tool loop with prompt-injection guards and tool-message pruning (pruneToolMessages 24k chars), SSE streaming with marker filtering, persistence + analysis enqueue.
invariants: markers filtered on the way OUT of the stream (split-across-tokens safe); empty completion must still produce a real answer (1852d96); every mutating route needs explicit authorize() (Viewer role exists); tool output wrapped as untrusted data before returning to model.
pitfalls: chat.service.ts is the hottest, largest file — changes ripple to voiceLlm.routes.ts which imports its internals (loadChatResources, buildSystemMessage, runToolLoop, computeScreening…); Gemini rejects reused/union JSON-schema subschemas (2684c25 prod incident) — sanitize via geminiToolSchema.ts; non-Gemini model ids were once silently rewritten to Gemini (header comment in modelProvider.ts).
confidence: verified

### api-voice-elevenlabs — Voice calls (custom-LLM bridge, legacy webhook, MCP server)
purpose: wire ElevenLabs Conversational AI agents to Botify brains; sync agent config/prompts/knowledge; import transcripts.
path_prefixes: packages/api/src/services/elevenlabs/
key_files: voiceLlm.routes.ts (custom-LLM endpoint, +test), agentConfigSync.ts (+agentConfigSync.customLlm.test.ts), voiceMcp.ts + mcpServer.routes.ts (+test), voiceTools.ts (legacy webhook tool), voiceTranscript.ts (post-call importer, dedupes metadata.source==='voice'), voicePrompt.ts, sourceSyncRunner.ts
entrypoints: POST /api/voice-llm/:agentId/completions AND /completions/chat/completions (both required — see pitfalls); POST /api/mcp/elevenlabs/:agentId (StreamableHTTP MCP).
responsibilities: per-turn OpenAI-SSE completions using the same brain as text chat; safety screening with useClassifier:false (latency); deterministic pending-action confirmation resolution; escalation handling with bilingual spoken fallback lines; message persistence tagged for transcript dedupe; agent provisioning/sync to ElevenLabs incl. custom_llm.url + ConvAI dynamic variables.
invariants: customLlm only for compliance.voice.customLlm===true agents (defense in depth); conversation correlation via OUR session row, never client-supplied identity tokens; VOICE budgets: 6 iterations, 12s tool timeout, 12s LLM timeout (dead air is the failure mode); already-handed-off conversations get empty utterance, never re-engaged.
pitfalls: the 404-every-turn bug — ElevenLabs appends `/chat/completions` to the base URL, so real turns hit `.../completions/chat/completions`; matching only the un-suffixed path broke EVERY call from day one until 49d4d73; IVC (Instant Voice Clone) voices cannot use custom_llm → automatic runtime fallback to legacy path (f9bd6d5); memory context was once missing here despite header claiming parity (fixed 3cee4ad).
confidence: verified

### api-knowledge — Knowledge ingestion & RAG
purpose: per-tenant knowledge sources → extraction → chunking → embeddings → pgvector retrieval; suggestions; scheduled recrawls.
path_prefixes: packages/api/src/modules/knowledge/, packages/api/src/services/knowledge/
key_files: modules/knowledge/{knowledge.service,knowledge.controller,suggestions.service}.ts, services/knowledge/{chunker,indexer,retrieval,reranker,extract,enrich}.ts (chunker/retrieval untracked = in-flight "engine v2"), services/crawler/engine.ts (new crawler), jobs/workers/{knowledge,knowledgeSync}.worker.ts
entrypoints: /api/agents/:agentId/knowledge/* routes; addKnowledgeJob → 'knowledge-processing' queue; repeatable differential recrawl sweep ('knowledge-sync').
responsibilities: PDF/DOCX/HTML/crawler extraction, RecursiveCharacterTextSplitter, Gemini embeddings (1536-dim), DocumentChunk storage, RAG search with injection guards (rag.injection.test.ts), conflict detection (knowledgeConflict.ts), optional push to ElevenLabs KB.
invariants: e2e tier guards slow/huge/wrong-type URL ingestion (4a98dde); embeddings provider auto-fallback (EMBEDDINGS_PROVIDER=auto|gemini).
pitfalls: migration 20260824120000_knowledge_engine_v2 uncommitted together with code — branch ships as a unit or not at all; single-URL ingestion was hardened after prod issues (see sha).
confidence: verified (v2 pieces strongly_inferred)

### api-integrations — Odoo / Dynatrace / Splunk / MCP / channel providers
purpose: native tool adapters + OAuth/connection lifecycle for customer systems; capability discovery; evidence normalization.
path_prefixes: packages/api/src/modules/{odoo,dynatrace,splunk,mcp,integrations}/, packages/api/src/services/{odoo,dynatrace,splunk,integrations}/
key_files: services/odoo/{agentTools,odooDomainTools,operationAccess,odooErrors,odooCapabilities}.ts(+tests), services/dynatrace/{agentTools,dynatraceClient,dynatraceDiscovery,dynatraceGrail,dynatraceErrors,dynatraceFormat,dynatraceCapabilities}.ts(+12 test files, __mock__/mockDynatraceServer.ts), services/integrations/{capabilityRegistry,accessPolicy,evidence,timeframe,evaluationSuites}.ts (untracked), services/integrations/core/ (oauth-state, token-vault e2e tests), services/mcp/
entrypoints: /api/odoo, /api/dynatrace, /api/splunk admin routers; tools loaded into chat loop via loadChatResources; provider registry populated by side-effect import in index.ts/workers-entry.ts.
responsibilities: per-connection credential vault (AES), SSRF guards (security/urlGuard.ts), scope/model-aware tool gating, Grail-DQL fallback for retired classic APIs, tenant isolation + rate limiting per connection, structured error envelopes replacing free-form strings (in flight).
invariants: Odoo writes go through deny-by-default policy.manifest.json + operation classes + actAs choke point; read degradation to acting-user-visible fields (38d0d34); Dynatrace "system error ≠ empty result" (d5c6955); Splunk SPL backtick-bypass guard (1061b33).
pitfalls: dynatrace_forecast was pulled after its execute path proved wrong LIVE (0b231ea) then re-added only after finding the real Davis Analyzers path (400b9bd) — verify execute paths against prod before shipping tools; missing scope warnings can be stale/false (956b22b: slo.read isn't even offered by Dynatrace's own token editor); policy.manifest.json must reach dist/ (5fc560e CRITICAL prod break).
confidence: verified (capabilityRegistry/evidence layer inferred from audit doc + filenames)

### odoo-addon — Botify Odoo module (Python)
purpose: in-Odoo addon providing signed nonce auth, delegation, policy enforcement at the source, so end-user mode enforces Odoo's own record rules.
path_prefixes: integrations/odoo/botify_agent/, integrations/odoo/policy/
key_files: __manifest__.py, controllers/, models/botify_policy.py, data/policy_manifest.json, security/, tests/
entrypoints: Odoo HTTP controllers called by packages/api/services/odoo.
responsibilities: nonce replay guard, delegation ledger w/ own expiry (c7a8cfc), deny-by-default manifest enforcement source-side, custom-model classification hooks (per-tenant policy 28203ba).
invariants: manifest version bumped on policy change (fcec602 → 2.1.0); Odoo 19 compat (res.users.groups_id removed — f4832d9; replay guard silently no-oping — 008eb05).
pitfalls: Odoo.sh "Test: Warning" build status noise (229749b); fixtures using removed fields fail on newer Odoo.
confidence: verified (structure), strongly_inferred (runtime behavior)

### api-outreach — Campaigns, journeys, audiences, push, social
purpose: multi-channel outbound marketing (email/push/social/WhatsApp/SMS lineage), segments, journeys automation, deliverability, consent/suppression.
path_prefixes: packages/api/src/modules/outreach/, packages/api/src/services/outreach/, packages/api/src/modules/{social,push}/
key_files: modules/outreach/*.routes|service, jobs/workers/outreach{Import,Segment,Compose,Send,Push}.worker.ts, journey.worker.ts, social.worker.ts, queue.ts outreach* + socialPublish/socialMetrics queues, ChannelHealth/EmailSendingDomain/SuppressionEntry models
entrypoints: /api/outreach (sub-routers segments/journeys/email-domains/push mount BEFORE the catch-all), public tracking/unsubscribe routes, /api/social, /api/push.
responsibilities: contact-list import, AI compose, rate-limited send (one recipient per job, delay-chained), A/B variants, journey enrollment/ticks, tracked links, suppression + MarketingConsent (GDPR), social publishing fan-out per target.
invariants: segment_enter enrolls each contact ONCE not every tick (3b6f-era campify fix carried forward); open-click redirect guard (fe24a94); consent gating.
pitfalls: this module was Campify rebuilt — old standalone app deleted; don't resurrect references from docs of that era.
confidence: strongly_inferred (module internals not read line-by-line)

### api-identity — End-user identity & durable memory
purpose: third auth concept (distinct from tenant JWT and platform-admin JWT): widget visitor identities, optionally verified via Odoo; sessions, assertions, RTBF retention.
path_prefixes: packages/api/src/services/identity/, packages/api/src/modules/identity/
key_files: services/identity/identity.service.ts (resolveIdentityBySessionId), modules/identity/*, ExternalIdentity/IdentitySession models, identityMemoryRetention.worker.ts
entrypoints: /api/chat/... identity routes (public), /api/identity admin router.
responsibilities: issue/bind sessions at call-start (stamped onto Conversation.identitySessionId), authorize Odoo end_user mode via actAs, gate durable cross-conversation memory facts to VERIFIED identities only.
invariants: anonymous visitors never get durable memory (trust boundary shared with Odoo end-user mode); identity always re-derived from our session id, never client-supplied token alone.
pitfalls: external_identity migration 20260731120000 added this late — older conversations lack identitySessionId (nullable everywhere).
confidence: verified

### api-platform-ops — Orgs, billing, RBAC, system config, notifications, files, reports/artifacts
purpose: tenant administration, custom billing/quota, plan catalog, platform-admin API surface, SystemConfig DB-backed settings, file generation, report artifacts.
path_prefixes: packages/api/src/modules/{organizations,platform,roles,team,auth,notifications,files,reports,analytics,booking,support,ai-studio,artifacts}/, packages/api/src/services/{plans,reports,email.ts,notifications.ts}
key_files: utils/config.ts (hot-reloaded SystemConfig + cluster invalidation), utils/orgFeatures.ts, middleware/orgFeature.ts, services/reports/artifacts.ts (untracked, +test), prisma/scripts/create-platform-admin.ts
entrypoints: /api/org, /api/platform (install gated by PLATFORM_INSTALL_TOKEN), /api/auth, /api/files, /api/artifacts, /api/reports.
responsibilities: Subscription rolling-period limits with threshold notifications; Plan/FeatureCatalog/PlanFeature dynamic plans; per-org feature flags resolved org.settings.features → plan catalog → hardcoded ORG_FEATURE_CATALOG seed in @chatagent/shared; CSV/Excel/PDF/Word generation (fileTools.ts) now upgraded to persisted ReportArtifact rows with provenance (in flight).
invariants: PlatformAdmin is a separate identity table + separate JWT secret (defaults derived from JWT_SECRET); first admin bootstrapped only while table empty; secrets encrypted via ENCRYPTION_KEY, decrypt at point of use only.
pitfalls: PUT /api/org/profile shipped without authorize() letting any member rename/rebrand workspace (CLAUDE.md lesson — check every mutating route); file links used to be effectively-permanent HMAC URLs with no lifecycle (audit finding #6).
confidence: verified (billing/RBAC), strongly_inferred (artifacts redesign)

### jobs-workers — Background processing tier
purpose: all BullMQ processors + periodic sweeps, runnable standalone in prod.
path_prefixes: packages/api/src/jobs/
key_files: jobs/queue.ts (13 queues), jobs/workers/*.worker.ts (24 files incl. alertMonitor, retention, auditRetention, subscriptionPeriod, tokenRefresh, integrationPoll, outlookSubRenewal, connectionHealth, odooEnvSync, odooOperations), jobs/conversationTimeout.ts
entrypoints: src/workers-entry.ts (dist/workers-entry.js under PM2 chatagent-workers).
responsibilities: knowledge processing/sync, conversation analysis + timeout sweeps, analysis-backfill, subscription period rollover, alert monitoring, retention/RTBF purges, integration polling/token refresh/health, Odoo env sync + operation execution, 5 outreach pipelines, journey ticks, social publish/metrics.
invariants: MUST be registered in BOTH index.ts and workers-entry.ts or it silently skips one environment; providers registry imported side-effect-style in both.
pitfalls: single-instance assumption — Redis distributed locks make >1 replicas safe-ish but default is 1; queue records trimmed (200 complete/500 failed) to avoid unbounded growth.
confidence: verified

### web-dashboard — Tenant web app (Next.js 16)
purpose: auth screens + full dashboard (agents, conversations, analytics, knowledge, integrations UI, outreach, settings) + SEO marketing site.
path_prefixes: packages/web/src/app/(app)/[locale]/, packages/web/src/app/(marketing)/[locale]/, packages/web/src/screens/
key_files: src/i18n/routing.ts (localePrefix:'always', localeDetection OFF), two root layouts ((marketing) SSR vs (app) dark-only class="dark"), src/i18n/locales/{en,ar}.ts (~3.5k lines each react-i18next) vs messages/{en,ar}.json (next-intl), screens/*.tsx (~30 pages), utils/supportWorkspace.ts (hasPermission sidebar mirror)
entrypoints: next start :5173 (PM2 chatagent-web), nginx reverse proxy (infra/nginx/botifyarabia.ai.conf).
responsibilities: bilingual ar/en with RTL, Socket.IO client for live conversations, TanStack Query over axios, Recharts charts, embed preview, legacy-path 308 redirects.
invariants: dashboard strings go in react-i18next locales, marketing strings in next-intl messages — two stores BY DESIGN; (app) is dark-only (no theme toggle; client-side .dark broke first paint); `<html lang>` static in (app), swapped client-side; sidebar nav mirrors server permission gates but server remains the gate.
pitfalls: robots must never bounce Googlebot off `/` (localeDetection off, `/`→`/ar`); setting .dark from client effect regresses first paint.
confidence: verified

### platform-admin — Platform owner console
purpose: manage orgs, billing, system config, feature catalog, integration tokens; separate identity + noindex everywhere.
path_prefixes: packages/platform-admin/src/app/
key_files: src/app/(console)/, login/, providers.tsx
entrypoints: next start :5174 (PM2 chatagent-admin), nginx admin.botifyarabia.ai.conf.
responsibilities: super/operator roles via PLATFORM_ADMIN_JWT_SECRET; org suspension (Auth rejects ALL requests when Organization.status==='suspended'); Dynatrace platform-level token mgmt (migration 20260616190000).
invariants: entire tree robots noindex/nofollow/nocache; never shares tenant auth.
pitfalls: none recorded beyond generic.
confidence: strongly_inferred

### widget — Embeddable chat widget
purpose: dependency-light vanilla-TS embeddable widget: chat, image upload, voice, handoff, per-agent theming; Shadow-DOM isolated.
path_prefixes: packages/widget/src/
key_files: main.ts (sets window.Shamsi after mount), core/{ChatWidget.ts,voice-loader.ts(+test),widget-markdown.ts,widget-settings.ts}, voice-entry.ts, styles/
entrypoints: two Vite lib-mode IIFE builds: widget.iife.js and widget-voice.iife.js (@elevenlabs/client); voice bundle injected by core/voice-loader.ts on FIRST voice call only.
responsibilities: Socket.IO + REST transport to public chat endpoints; draggable position persistence; quick replies, custom CSS; streams errors surfaced (d62ff51 fixed silent swallowing).
invariants: keep the dual-IIFE build — a plain import() cannot replace it because Vite lib-mode forces inlineDynamicImports for single-file IIFE output and would fold the SDK back into the main bundle.
pitfalls: patch_widget*.js / fix_widget.js at repo root are one-off codemods from drag-feature development — historical debris, not product code.
confidence: verified

### shared-and-deploy — Shared types, CI, deploy tooling
purpose: cross-package constants/types (systemConfigKeys.ts, ORG_FEATURE_CATALOG); deploy scripts with guardrails.
path_prefixes: packages/shared/src/, deploy/lib/, scripts/, .github/workflows/, ecosystem.config.cjs, deploy.sh
key_files: shared/src/systemConfigKeys.ts, deploy/lib/{migration-guard,snapshot,health-check}.sh, scripts/logs.sh, scripts/eval-*.{mjs,cjs} (production eval harnesses), eslint flat config
entrypoints: npm scripts at root; bash scripts/logs.sh streams PM2 logs over SSH.
responsibilities: turbo task graph; CI quality job (pgvector+Redis services → prisma db push → turbo build lint test → test:e2e step) + docker build-only on master; manual deploys ship prebuilt artifacts with DROP-refusing migration guard, pre-deploy pg_dump snapshot, /api/ready health poll + rollback.
invariants: deploy.sh does NOT build (step-0 guard) nor install new deps on the server; SKIP_* env knobs documented bypasses.
pitfalls: turbo strict env needs globalPassThroughEnv entries (19b1df4); docker must copy prisma schema before npm ci (postinstall generates client — b538fcf).
confidence: verified

## FLOWS
### Text chat turn (public widget or dashboard)
trigger: user sends message via REST/SSE.
steps:
1. POST /api/chat/... → agent-origin validation (assertAgentOriginAllowed, per-agent allowed origins).
2. Optional identity resolution from session/token (services/identity).
3. resolveWorkspaceAi: agent override → org default → platform SystemConfig default (provider/model/key).
4. loadChatResources: pgvector RAG retrieval IN PARALLEL with tool loaders (MCP MultiServerMCPClient w/ decrypted headers, custom HTTP actions w/ confirmation state, file tools, Odoo/Dynatrace/Splunk bundles), memory contexts folded in.
5. buildSystemMessage (personality, compliance, grounding reminders, current date f829674).
6. runToolLoop ≤10 iterations, 5 parallel calls, per-tool timeouts, tool-output pruning, untrusted-data wrapping; Gemini schema sanitization.
7. Token stream through createStreamMarkerFilter ([ESCALATE_TO_HUMAN], DOC citations stripped even mid-token).
8. Persist Conversation/Message rows; Socket.IO emit (redis adapter fan-out); enqueue conversation-analysis job (3s delay).
files: packages/api/src/modules/chat/chat.service.ts, services/ai/*.ts, services/realtime/conversationRealtime.ts
confidence: verified

### Voice call turn (custom-LLM path — the deploy branch centerpiece)
trigger: ElevenLabs Conversational AI agent POSTs OpenAI-shaped request per spoken turn.
steps:
1. Route matches BOTH /api/voice-llm/:agentId/completions and .../completions/chat/completions (ElevenLabs SDK appends suffix).
2. Auth: X-API-Key vs agent's elevenlabs integration credentials (timing-safe compare); agent must have compliance.voice.customLlm===true.
3. Correlate X-App-Conversation-Id (ConvAI dynamic variable) to our Conversation row; reject if foreign; re-derive identity from conv.identitySessionId.
4. If humanHandoffAt && !supportResolvedAt → empty utterance (never re-engage AI mid-handoff).
5. assertMessageQuota; mapOpenAiMessagesToHistory splits trailing user turn vs ≤20 history.
6. Safety screening lexicon-only (useClassifier:false for latency); containment/handoff short-circuits speak fixed bilingual lines.
7. Pending high-risk action confirmations resolved deterministically from "yes/no" reply (else infinite ask-loop).
8. loadChatResources + buildSystemMessage('voice') + runToolLoop (≤6 iters, 12s tool/LLM timeouts) streamed via marker filter; no-tools branch streams directly w/ AbortSignal.timeout + non-streamed retry.
9. Escalation detected from RAW accumulated text; stripDocCitations; empty answer → spoken fallback (never silence).
10. Persist both turns tagged metadata.source==='voice' (voiceTranscript.ts dedupe depends on tag); escalation triggers requestHumanHandoff.
files: packages/api/src/services/elevenlabs/voiceLlm.routes.ts, agentConfigSync.ts, modules/chat/chat.service.ts
confidence: verified

### Knowledge ingestion
trigger: tenant adds/updates KnowledgeSource (URL/upload) or scheduled recrawl sweep fires.
steps:
1. knowledge.controller → knowledge.service creates source → addKnowledgeJob('knowledge-processing').
2. Worker extracts content (PDF/DOCX/HTML/puppeteer crawler engine).
3. Chunk (RecursiveCharacterTextSplitter / engine-v2 chunker) → enrich → Gemini embeddings → DocumentChunk rows.
4. Optional ElevenLabs KB sync (syncElevenlabs flag); conflicts flagged (knowledgeConflict.ts); suggestions generated.
5. knowledge-sync queue runs differential 'sweep'/'sync-source' recrawls on schedule.
files: modules/knowledge/*, services/knowledge/*, jobs/workers/{knowledge,knowledgeSync}.worker.ts
confidence: verified (pipeline), strongly_inferred (engine-v2 specifics)

### Outreach send
trigger: campaign approved/scheduled, or journey step due.
steps:
1. Segment materialized via outreachSegmentQueue (AI-assisted, dedup enrollment).
2. outreachComposeQueue drafts variants (A/B) with merge tags per contact.
3. Send fan-out: ONE recipient per outreachSendQueue job, re-enqueued with delayMs to enforce per-hour rate without long locks; push analog fans per-device PushDelivery jobs.
4. Tracking pixels/tracked-link clicks → OutreachEvent; suppressions and consents checked upstream; ChannelHealth updated.
5. Journey ticks (repeatable 60s) find due JourneyRuns → per-run jobs.
files: jobs/queue.ts, jobs/workers/outreach*.worker.ts, journey.worker.ts, modules/outreach/*
confidence: strongly_inferred

### Production deploy (manual)
trigger: human runs ./deploy.sh after npm run build.
steps:
1. Guard: artifact exists (ships artifacts, doesn't build).
2. Migration guard: prisma migrate diff containing DROP aborts unless SKIP_MIGRATION_GUARD=1.
3. Pre-deploy pg_dump snapshot (deploy/lib/snapshot.sh, path recorded ~/app/.last_predeploy_backup).
4. rsync to EC2 → prisma migrate deploy + generate ON SERVER → pm2 restart (or reload api) → poll /api/ready (deploy/lib/health-check.sh) with documented rollback.
files: deploy.sh, deploy/lib/*.sh, ecosystem.config.cjs
confidence: verified

## APIS
Conventions: Express routers per module `*.routes.ts` → `*.controller.ts` → `*.service.ts` with Zod validation (middleware/validate.ts); tenant JWT cookie auth (`authenticate`) + permission strings (`authorize('support:inbox')`); platform routes use platformAuth/platformSuper; public endpoints gated by agent-origin or per-agent shared secrets; errors via typed errors → errorHandler; ~100+ routes total — representatives below.

| method | route | handler file:symbol | auth | notes |
|---|---|---|---|---|
| GET | /api/health, /api/ready, /api/metrics | app.ts:createApp | none | ready checks DB/Redis; deploy gate |
| POST | /api/auth/register\|login\|refresh | modules/auth/* | none | httpOnly JWT cookies |
| GET/POST/PATCH | /api/agents/:id/... | modules/agents/agent.controller | tenant+authorize | includes knowledge/actions/analytics/integrations submounts |
| POST | /api/chat/agent/:agentId/message(+stream) | modules/chat/chat.controller:sendMessage/Stream | public (origin check) | hot path |
| POST | /api/chat/:conversationId/close \| rating | chat.controller | mixed | closes → analysis job |
| POST | /api/voice-llm/:agentId/completions(+ /chat/completions) | services/elevenlabs/voiceLlm.routes.ts:POST handler | X-API-Key (integration secret) + customLlm flag | OpenAI-SSE contract |
| POST | /api/mcp/elevenlabs/:agentId | services/elevenlabs/mcpServer.routes.ts | X-API-Key | discrete booking/handoff tools |
| POST | /api/webhooks/elevenlabs/... | modules/integrations/webhook.routes | X-API-Key | legacy whole-brain tool path |
| GET/POST | /api/integrations/connections, /oauth, /catalog | modules/integrations/* | tenant+authorize | OAuth state, token vault |
| CRUD | /api/org/profile etc | modules/organizations/* | tenant+authorize | authorize() was MISSING historically (lesson) |
| * | /api/odoo, /api/dynatrace, /api/splunk | modules/{odoo,dynatrace,splunk}/* | tenant+authorize | connection admin + tool catalogs |
| POST | /api/platform/install | modules/platform/* | PLATFORM_INSTALL_TOKEN | only while platform_admins empty |
| GET | /api/widget/:agentId/config | modules/ widget routes | public | drives widget appearance |
| POST | /api/files/generate, /api/artifacts | modules/files, modules/artifacts | tenant | file/report generation |
| * | /api/outreach/{segments,journeys,email-domains,push}, /api/outreach | modules/outreach/* | tenant+authorize | sub-routers BEFORE catch-all |
| POST | /api/push/key\|subscribe | modules/push | public | VAPID subscribe |

## DATABASE
Engine: PostgreSQL 16 with pgvector (pgvector/pgvector:pg16 image, local port 5433); Prisma 6 ORM; Redis 7 (BullMQ + rate-limit + pub/sub config invalidation + socket adapter); MinIO/S3 object storage (bucket chatagent-files).
Scale: prisma/schema.prisma 1929 lines, 66 models. Migrations: 55 SQL dirs; notable — `20260401000000_baseline` (untracked, fresh baseline being introduced on this branch), hot_path_indexes (20260716160000), external_identity, conversation_memory, knowledge_engine_v2, odoo_enterprise_ledger_and_delegation, odoo_tenant_model_policy, dynatrace_workflow_allowlist, report_artifacts, splunk_attachment_index_scope, reconcile_legacy_schema_drift (drift-repair pattern), drop_stale_conversation_id_index, native_integration_access_mode.
Notable entities WITH MEANING: Organization (tenant root; settings.features feature flags; status='suspended' blocks all auth), User+Role/RolePermission/UserRole (RBAC, string perms like support:inbox; isOrgOwner bypass), PlatformAdmin (separate staff identity), Agent+AgentConfig (systemPrompt, personality, compliance{voice.customLlm, safetyScreening}), KnowledgeSource/KnowledgePage/KnowledgeSyncRun/KnowledgeSuggestion (ingestion lifecycle), DocumentChunk (vector(1536) Unsupported column, HNSW cosine), Conversation/Message (metadata.toolCalls/attachments; identitySessionId; humanHandoffAt/supportResolvedAt), ConversationAnalysis (post-close satisfaction/sentiment/QA scores), ExternalIdentity/IdentitySession (widget visitor + verified Odoo identity), AgentIntegration/McpServer/AgentMcpServer (BYO MCP), IntegrationConnection/OAuthState/AgentChannel (generic channels incl. Meta/X/LinkedIn), OdooConnection/AgentOdooConnection/OdooOperation/OdooAuditEvent (enterprise ledger, approvals, idempotency), DynatraceConnection(+platform token)/SplunkConnection (+Agent* join tables), Subscription (rolling-period message/voice-minute/storage limits), Plan/FeatureCatalog/PlanFeature (dynamic plans), OrgBillingSettings (markup/flat fee), SystemConfig (DB-backed env override, hot-reloaded), AuditLog, ContactList/OutreachContact/Segment/Campaign/CampaignRecipient/CampaignVariant/Journey/JourneyRun/TrackedLink/SuppressionEntry/MarketingConsent/ChannelHealth/EmailSendingDomain/WhatsAppTemplate (outreach family), PushSubscriber/PushDelivery, SocialAccount/SocialPost/SocialPostTarget, ConsentRecord (GDPR), DemoBookingSettings/DemoAppointment (voice booking tools), ReportArtifact (NEW: artifact lifecycle replacing raw HMAC links).
RLS/policies: none in Postgres — isolation enforced application-side by orgId filtering (regression: src/__e2e__/tenant-isolation.e2e.test.ts); Odoo-side enforcement via addon record-rules/policy manifest instead. Vector store = pgvector only. Caches: SystemConfig in-memory w/ Redis cluster invalidation; Dynatrace read caches.
No secrets are stored plaintext: credentials AES-encrypted (utils/encryption.ts, ENCRYPTION_KEY), decrypted at point of use.

## TESTS
Frameworks: Vitest 4 everywhere; Supertest for HTTP-level specs; NO component/E2E browser tests for frontends (1 test each in web/platform-admin).
Commands: `npm test` (turbo; infra-free), `npm run test:e2e` (needs docker-compose Postgres+Redis), single: `cd packages/api && npx vitest run src/path/x.test.ts [-t name]`.
Layout rule: unit tests MUST live under src/** matching `src/**/*.test.ts`; DB-bound specs suffixed `*.e2e.test.ts` excluded from default run (vitest.config.ts vs vitest.e2e.config.ts). CI runs tiers as separate steps with pgvector+Redis service containers.
Counts (verified): api 147, widget 2, web 1, platform-admin 1 ≈ 152 total. e2e set: tenant-isolation, oauth-state, token-vault, byoa, webhook.legacy, phase1 smoke.
Coverage mapping: chat/tool-loop/stream-marker/usage tests beside chat.service; geminiToolSchema/modelProvider/memory/safetyScreening/rag.injection in services/ai; dynatrace has the deepest suite (12+ files: grail fallbacks, scope gating, invalid-query correction, format); odoo has tenant-isolation/domain-tools/errors/operationAccess suites; workers have knowledge/auditRetention/odooOperations/retention.parse tests; eval harnesses in scripts/eval-* (live production evaluation, not CI).
Convention worth keeping: any new test needing Postgres/Redis gets renamed *.e2e.test.ts rather than making the default tier require docker.

## GIT LESSONS
Durable lessons (sha evidence):
- d5c6955 — "system error, not empty result" applied to the GENERIC tool-error path after fixing it per-tool: error taxonomy belongs in shared plumbing, not per-adapter patches.
- 49d4d73 — custom-LLM voice 404'd on EVERY turn from day one: the registered base URL got ElevenLabs' SDK `/chat/completions` suffix appended. Lesson: match the suffixed path too; confirmed live before shipping a new protocol bridge.
- 2684c25 — Gemini 400s on reused/union JSON-schema subschemas (prod incident): sanitize tool schemas per provider (geminiToolSchema.ts).
- 0b231ea → 400b9bd — pulled dynatrace_forecast when its execute path failed live, re-added only after finding the real Davis Analyzers path: don't ship tools whose happy path wasn't executed against prod.
- 5fc560e — CRITICAL: policy.manifest.json never reached dist/ breaking every Odoo tool call in prod — tsc copies only TS outputs; static assets need copy-static-assets.js (build script now does `tsc && node scripts/copy-static-assets.js`). Any new non-TS runtime asset repeats this trap.
- ab897e1/635c3a9 + earlier PR #38 merge — Campify was built as a ~70-commit standalone product, merged, then REMOVED wholesale from master and rebuilt as the outreach module. Durable lesson: standalone spin-offs got abandoned; features belong inside the monorepo.
- 7573b92 + deploy.sh note — Next `output:'standalone'` + next-intl middleware = absolute x-middleware-rewrite turned into infinite 307 loop on every unprefixed (Arabic) path; build stayed green, only deployed artifact broke. Keep `next start`.
- modelProvider.ts header comment — provider selection once silently rewrote non-Gemini model ids to a Gemini default; multi-provider routing is real, don't reintroduce single-vendor assumptions.
- CLAUDE.md-recorded incident — `PUT /api/org/profile` shipped with authenticate but no authorize(): any Viewer could rename/rebrand a workspace. Every mutating route needs explicit permission.
- 008eb05/f4832d9 — Odoo major-version upgrades break addons silently (removed res.users.groups_id; nonce replay guard no-op): test addons against the actual Odoo version.
- 437458c/0ed64f5/c2bb5fb — streaming crash recovery series: guard the ACTUAL crash site; fall back to non-streaming invoke when a stream dies before first chunk; recover mid-stream @langchain/google-genai tool-call crashes.
- fe39561/d62ff51 — widget stream errors were silently swallowed (the reported "hangs"); surface errors client-side and log stream-request failures server-side (0a3aba1).
Dangerous areas: chat.service.ts (every change ripples to voiceLlm + playground); app.ts route-mount ORDER (outreach catch-all); the dual worker-registration files; dist asset copying; prod box memory (~900MB, ceilings cause restart loops not capacity — ecosystem.config.cjs comments).
Reverted approaches: dynatrace_forecast v1 execute path (pulled); Campify standalone (deleted); quiet-hours logic removed (a6475ef); CodeQL + dependabot removed (f81bd79/1b042bd); AWS deployment guide removed early.

## DECISIONS
- npm workspaces + turbo, not pnpm — brief/task descriptions say pnpm but repo standardizes npm 10.8.0 (root package.json, package-lock.json) — evidence: package.json:34, README, CI `npm ci`.
- Split worker tier via START_WORKERS=false rather than separate codebase — same code registers in two entrypoints; tradeoff documented as the likeliest silent-failure trap — evidence: src/index.ts, src/workers-entry.ts, ecosystem.config.cjs.
- Custom-LLM voice bridge over extending the webhook-tool path — one LLM round trip instead of two, exact text-chat brain reuse (RAG/tools/safety/memory) — evidence: voiceLlm.routes.ts header comment, agentConfigSync.customLlm.test.ts.
- Two translation stores (next-intl marketing / react-i18next dashboard) and two root layouts — deliberate: localePrefix:'always' + localeDetection off protects SEO; (app) dark-only avoids first-paint theme flash — evidence: packages/web/src/i18n/routing.ts, layouts, CLAUDE.md.
- No Stripe — custom Subscription rolling-period quotas with notification thresholds — evidence: Subscription/OrgBillingSettings models, assertMessageQuota/assertVoiceQuota.
- Deny-by-default Odoo policy manifest enforced at SOURCE (addon) + API layer, with per-tenant custom-model classification — evidence: integrations/odoo/policy/, migrations 20260901000000/20260908000000, commits 7bf8723/28203ba/f5ede8a.
- Risk-tiered confirmation gate for custom HTTP actions; deterministic confirmation resolution in BOTH chat and voice turns — evidence: services/ai/customActions.ts, 129ea16, voiceLlm step 7.
- Ship artifacts not builds; refuse destructive migrations; snapshot before deploy; gate on /api/ready — evidence: deploy.sh, deploy/lib/*.
- Frontends stay Node servers (no standalone output, no static export) for locale routing/redirects/image optimization — evidence: ecosystem.config.cjs comments, commit 7573b92.
- Infra-free unit tier vs DB-bound e2e tier naming convention (*.test.ts vs *.e2e.test.ts) — evidence: vitest.config.ts comments, CI workflow.

## RISKS & TECH DEBT
- 144 uncommitted files on the deploy branch including 7 migrations, the whole knowledge-engine-v2, capability/evidence layer, and ReportArtifact redesign — huge blast radius if partially committed or lost; ship/review as coherent units. Evidence: git status.
- docs/integrations/architecture-audit-2026-08-24.md documents UNFIXED root causes: no universal capability contract, discovery≠effective-access, generic orchestration without typed investigation plans, string-typed tool results, Odoo large-export bypassing chat authorization path (services/reports/odooRows.ts uses service credential, ignoring allowRead/actor context) — a real authorization asymmetry between chat answers and exported reports.
- chat.service.ts at 2562 lines is a god-module consumed by voiceLlm.routes.ts; refactors risk breaking three surfaces at once.
- Dual worker registration (index.ts vs workers-entry.ts) has no compile-time guard — a worker added to one file silently never runs in the other environment.
- Prod capacity: ~900MB box hosting postgres+redis+nginx+4 PM2 apps; memory ceilings convert OOM to restart loops (ecosystem.config.cjs warning block).
- Widget root debris: patch_widget.js, patch_widget2.js, fix_widget.js, test_chat.ts at repo root are one-off codemods/scripts that should be archived or deleted.
- Baseline migration `20260401000000_baseline` + `reconcile_legacy_schema_drift` suggest history of schema drift between environments; migration discipline matters on this branch.
- ElevenLabs system tools (end_call, skip_turn, language_detection) ignored on custom-LLM path — documented ponytail cut; add when needed (voiceLlm.routes.ts header).
- Rate limiter disabled in dev by default — prod-only behaviors (800/15m IP limit) can surprise newly-shipped public endpoints.
- Single EC2 + PM2 fork mode, no container orchestration; deploy.sh ships code but NOT new node_modules (deps must be installed on server manually first).

## UNCERTAIN
- Exact runtime behavior of the UNTRACKED in-flight services (capabilityRegistry, accessPolicy, evidence, evaluationSuites, knowledge engine v2 chunker/reranker/retrieval, reports/artifacts) — inferred from filenames + audit doc + tests existing; not read line-by-line.
- Whether the baseline-migration strategy (20260401000000_baseline squashing prior history) is intended to replace the 50+ historical migrations on merge, and how reconcile_legacy_schema_drift interacts with prod state.
- modules/{booking,ai-studio,artifacts,support,reports} internals were mapped only via names/routes; responsibilities summarized from routes and doc references.
- Frontend page inventory beyond the ~30 screen names listed; i18n coverage completeness not audited.
- Python addon test suite depth (integrations/odoo/botify_agent/tests) not inspected.
- Total LOC and the "~18G" size claim (node_modules dominated; not measured).
- Whether deploy-staging.yml workflow is actually wired to infrastructure or vestigial (file exists; contents not read past ci.yml).
- Historical commits before 467-commit window: earliest commits have placeholder messages ("-" at 3ae5e4d); early project intent inferred from later structure.
