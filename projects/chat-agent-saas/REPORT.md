# chat-agent-saas — Engineering Examination (Botify)

Generated 2026-08-25 from a full read of the working tree at `deploy/voice-custom-llm-2026-08-19`. Every non-obvious claim cites a path; line refs (`file.ts:123`) are from this commit and will drift.

## META

| Field | Value |
|---|---|
| Repo path | `/home/aboud/Dev/chat-agent-saas` |
| HEAD sha | `1ed44277b38191790eca5a57f3b3eed3cf8250a4` |
| Branch | `deploy/voice-custom-llm-2026-08-19` |
| Dirty files | 1 — `D CLAUDE.md` (deleted in working tree, still tracked in HEAD) |
| Examined | 2026-08-25 |
| Workspaces | npm workspaces `packages/*` (root `package.json:4-6`): `api`, `web`, `widget`, `platform-admin`, `shared`. There is **no** top-level `apps/` directory despite the README's "monorepo" phrasing — everything lives under `packages/`. |
| Orchestration | Turborepo 2.9; tasks `build` (dependsOn `^build`), `dev`, `lint`, `test`; `globalPassThroughEnv` whitelists DB/Redis/AI env vars into task processes (`turbo.json:3-33`). Root scripts: `dev`, `build`, `lint`, `test`, `test:e2e`, `db:migrate`, `db:seed`, `logs` (`package.json:7-20`). |
| Node | `>=20`, packageManager `npm@10.8.0` (`package.json:34-37`) |

## OVERVIEW

Botify (© Botify Arabia, `README.md:1-7`) is a multi-tenant SaaS platform for building embeddable AI **chat and voice agents**: an enterprise connects its website/docs as a knowledge base (سجل المزامنة surfaces crawl history in the dashboard), configures an agent (persona, model, tools), and embeds a `<script>` widget — or wires WhatsApp/Telegram/Messenger/etc. channels — so end customers get RAG-grounded, tool-calling answers with human handoff, analytics, and outbound marketing ("AI Outreach"/Campaign Manager). Inbound STOP replies in Arabic (إلغاء) are honored as opt-outs by the shared inbound pipeline.

User types: **platform admins** (separate `PlatformAdmin` identity, `prisma/schema.prisma:66-81`), **org users** (tenant staff with RBAC roles, `schema.prisma:83-110` + `Role/UserRole` tables), **agents** (the tenant's configured bots, not humans), and **end customers** — either anonymous widget visitors or *verified external identities* asserted by a source platform like Odoo (`ExternalIdentity`/`IdentitySession`, `schema.prisma:512-594`).

Core value loop end to end: a customer's message arrives via the widget (`packages/widget`) or a channel webhook → the Express API validates origin/quota, resolves or creates a `Conversation` → `loadChatResources` runs pgvector hybrid retrieval **in parallel with** tool-bundle loading (MCP, Odoo, Dynatrace, Splunk, custom actions, file tools — `modules/chat/chat.service.ts:1199`) → `runToolLoop` drives a Gemini/OpenAI/Claude tool-calling loop bounded by timeouts and iteration caps (`chat.service.ts:422`) → the answer streams back over SSE while messages persist to Postgres and fan out over Socket.IO (`services/realtime/conversationRealtime.ts:128`) → on close, a BullMQ job analyzes the transcript for satisfaction/QA scores and mines knowledge suggestions (`jobs/workers/analysis.worker.ts`). Voice calls run the same brain through an OpenAI-compatible custom-LLM endpoint that ElevenLabs calls per turn (`services/elevenlabs/voiceLlm.routes.ts`). The same platform then re-targets those customers through Campaign Manager (email/WhatsApp/push/social journeys) with suppression and consent gates (`services/outreach/safety/*`).

## ARCHITECTURE

### Process topology
- **API tier**: `packages/api/src/index.ts` boots: `load-env` → Sentry init before other side effects (`index.ts:1-5`) → `validateEnvSecrets()` → `preloadConfigs()` (SystemConfig table into memory, `utils/config.ts:56-74`) → `preloadPlanCatalog()` → `createApp().listen(PORT||3000)`.
- **Workers**: in-process by default (`START_WORKERS !== 'false'`, `index.ts:50`); prod sets `START_WORKERS=false` on `chatagent-api` and runs a dedicated `chatagent-workers` process via `src/workers-entry.ts` (identical worker list, `workers-entry.ts:58-82`). PM2 definitions for four apps (`chatagent-api`, `chatagent-workers`, `chatagent-web`, `chatagent-admin`) with explicit capacity warnings live in `ecosystem.config.cjs`.
- **Realtime**: Socket.IO attached to the same HTTP server (`app.ts:123-140`) with `@socket.io/redis-adapter` so room emits cross PM2 workers/nodes. JWT-authenticated sockets join `user:{id}:notifications`; guests join `conv:{id}` after an ownership check (`conversationRealtime.ts:37-126`).
- **Queues**: BullMQ over Redis — 13 queues declared in `jobs/queue.ts:18-31`: `knowledge-processing`, `knowledge-sync`, `conversation-analysis`, `integration-token-refresh`, `integration-poll`, `outreach-import/-segment/-compose/-send/-push`, `journey-tick`, `social-publish`, `social-metrics`. Defaults: 3 attempts, exponential 30s backoff, keep last 200 completed / 500 failed (`queue.ts:7-16`).
- **Worker inventory** (all started in both entries, each idempotent): knowledge ingestion (`knowledge.worker.ts`) + scheduled recrawl sweeper (`knowledgeSync.worker.ts`); conversation analysis + backfill (`analysis.worker.ts`, `conversationTimeout.ts` which also owns the idle-handoff sweeper via setInterval); subscription period rollover (`jobs/subscriptionPeriod.ts`); alert monitor, retention, audit retention, identity-memory retention (`workers/{alertMonitor,retention,auditRetention,identityMemoryRetention}.worker.ts`); integration tier — OAuth token refresh (delayed per-connection jobs), poll-based channels, Outlook subscription renewal, connection health, Odoo env sync + operation executor (`tokenRefresh/integrationPoll/outlookSubRenewal/connectionHealth/odooEnvSync/odooOperations.worker.ts`); Campaign Manager five queues + journey + social two-queue sweepers (`outreachImport/Segment/Compose/Send/Push`, `journey.worker.ts`, `social.worker.ts`).
- **Deploy target**: EC2 + PM2 + nginx; `deploy.sh` = migration guard (refuses `DROP` diffs) → pre-deploy `pg_dump` → rsync built artifacts → `prisma migrate deploy` on server → PM2 restart → `/api/ready` health gate (`deploy.sh:1-40`, `README.md:117-127`). Data plane: PostgreSQL+pgvector, Redis, S3/MinIO via docker-compose locally (`docker-compose.yml`); nginx configs in `infra/nginx/`.

### Request lifecycle (middleware order in `app.ts`)
`createApp()` (`app.ts:93`) composes, in order:
1. `trust proxy 1` (`app.ts:95`)
2. `helmet` with CORP disabled (`app.ts:142-146`)
3. `compression` filtered to skip `text/event-stream` so SSE tokens aren't buffered (`app.ts:149-155`)
4. **custom dynamic CORS** (`app.ts:156-189`): no-Origin requests pass; platform origins pass; otherwise if the path names a public agent (`extractAgentIdFromPublicPath`, `modules/agents/agent-origin.service.ts:111-118`) the per-agent allowlist is checked; `/api/push/*` collector allows any origin without credentials; everything else is rejected.
5. `cookieParser`
6. `express.json({limit:'10mb'})` with a `verify` hook stashing `rawBody` **only** for `/api/webhooks/*` and `/api/integrations/webhook*` paths for HMAC verification (`app.ts:191-205`)
7. `express.urlencoded`
8. `requestLogger` → `metricsMiddleware` → global `rateLimiter` (Redis store, tenant-or-IP keying with *verified* JWT orgId to prevent cross-tenant bucket poisoning, `middleware/rateLimiter.ts:35-64`)
9. infra routes `/api/health`, `/api/ready` (DB+Redis probes w/ 3s timeout, `app.ts:217-237`), `/api/metrics` (queue depths + per-route latency, `app.ts:240-277`), `/api/openapi.json`, `/api/docs`
10. ~30 module routers (see APIS)
11. `Sentry.setupExpressErrorHandler` (if DSN) then `errorHandler` (`app.ts:356-361`)

### Shared package dependency graph (verified via package.json imports)
- `@chatagent/shared` ← imported by `api`, `web`, `widget` (each `package.json` lists `"@chatagent/shared": "*"`). **platform-admin does not depend on shared** (its `package.json` has no reference; verified by grep). shared itself has zero runtime deps (`packages/shared/package.json`).
- shared exports types (`types/*.ts`), permissions/roles defaults, plan constants, Gemini model catalog (`constants/models.ts`: `EMBEDDING_MODEL='gemini-embedding-001'`, dims 1536, `ANALYSIS_MODEL='gemini-2.5-flash'`), org feature flags, and the integration catalog incl. `GENERIC_HTTP_CONNECT_CATALOG_IDS` (currently an empty set, `constants/integrationCatalog.ts:77`).
- api→web coupling: none at build time; the widget talks only HTTP/Socket.IO to the API. web proxies `/api` via axios baseURL `${NEXT_PUBLIC_BASE_PATH}/api` (`packages/web/src/services/api.ts:14-19`).

### API-internal layering
`src/` is organized as: `modules/<domain>/{*.routes,*.controller,*.service,*.schemas}.ts` (HTTP surface) → `services/*` (domain engines shared by routes AND workers: ai, knowledge, integrations, odoo, elevenlabs, mcp, identity, realtime, outreach, plans, security, transcript, alerts, crawler, email) → `jobs/{queue,workers}/*` (BullMQ) → `middleware/*` → `utils/*` (prisma, redis, encryption AES-256-GCM, config, s3, logger pino, metrics, errors taxonomy, sentry). Two entry points (`index.ts`, `workers-entry.ts`) import the same services/workers; workers must never be started twice per process — every `start*Worker()` is idempotent via a module singleton (pattern shown in `analysis.worker.ts:41-51`). `services/integrations/providers` is imported for side-effect provider registration in BOTH entries or poll/token-refresh tiers silently no-op (`index.ts:38-39`, `workers-entry.ts:48-51`). An OpenAPI document is generated from code at `openapi.ts` and served at `/api/openapi.json` with CDN-hosted Swagger UI (`app.ts:281-291`).

### Frontends
- **web** (tenant dashboard + marketing): Next.js 16 App Router, React 19, next-intl (ar/en), Zustand stores (`stores/authStore.ts`, `stores/agentStore.ts`), TanStack Query, Recharts, socket.io-client. Route groups: `(marketing)/[locale]/*` (landing/pricing/features/articles…) and `(app)/[locale]/{dashboard,demo,login,register,…}` with `dashboard/[agentId]/…` per-agent screens (`packages/web/src/app/**`). Screens list (`src/screens/`): AgentConfig, AnalyticsPage, ConversationsPage, KnowledgeBasePage, IntegrationsPage, Odoo/Dynatrace/Splunk pages, Outreach/Segments/Journeys/Deliverability, SupportInboxPage, IssuesPage, PlaygroundPage, EmbedPage, TeamPage, etc.
- **platform-admin**: Next.js 16 console `(console)` screens for orgs/billing/plans/system-config/platform-admins (`packages/platform-admin/src/screens`).
- **widget**: framework-free Vite IIFE, Shadow-DOM isolated; entry reads `data-agent-id` off the script tag and mounts `ChatWidget`, exposing `window.Shamsi` (`packages/widget/src/main.ts:3-15`); separate voice entry + loader for ElevenLabs WebRTC voice (`src/voice-entry.ts`, `src/core/voice-loader.ts`).

### Hot-file map (where agents should look first)
| Concern | File |
|---|---|
| Chat brain / tool loop | `packages/api/src/modules/chat/chat.service.ts` (2562 lines) |
| Prompt assembly & guards | `chat.service.ts:188`, `services/ai/{personalityPrompt,rag}.ts` |
| RAG retrieval SQL | `services/knowledge/retrieval.ts` |
| Model routing | `services/ai/modelProvider.ts`, `resolveWorkspaceAi.ts` |
| Webhook entry (legacy/v2) | `modules/integrations/webhook.routes.ts`, `webhook-v2.routes.ts` |
| Voice custom-LLM | `services/elevenlabs/voiceLlm.routes.ts` |
| Identity exchange | `services/identity/identity.service.ts` |
| Auth/RBAC | `middleware/auth.ts`, `modules/auth/auth.service.ts` |
| Queue definitions | `jobs/queue.ts`; worker starts `index.ts:59-88` |
| Schema | `packages/api/prisma/schema.prisma` |

## MODULES

### auth & session (dashboard identity)
- Paths: `modules/auth/*`, `middleware/auth.ts`, `middleware/platformAuth.ts`, `middleware/platformSuper.ts`.
- Login: bcrypt(12) compare; per-account lockout counters in Redis with in-process fallback (`auth.service.ts:36-93`); email OR phone lookup (`auth.service.ts:367-384`); unverified email and suspended/deleted org rejected. Tokens: 15m access JWT + 7d refresh JWT (refresh stored single-copy in Redis `refresh:{userId}`, rotated each refresh, `auth.service.ts:97-144,431-475`); payload carries `tv` tokenVersion — bumped on password reset/sign-out-all/org suspension to invalidate cluster-wide (`auth.service.ts:602-634`, schema comment `schema.prisma:95-97`). `authenticate` re-reads the user each request and checks `tokenVersion`, `disabledAt`, org `deletedAt`/`status` in one query (`middleware/auth.ts:43-70`).
- Authorization: string permissions resolved from non-expired `UserRole→Role→RolePermission`; org owner bypasses (`authorize`, `middleware/auth.ts:102-140`); `authorizeAny` for OR-semantics; support-inbox permission implied by agents:create/update/delete (`userSatisfiesPermission`, `middleware/auth.ts:9-19`).
- Invariant: expired role assignments must never grant permissions (`activeUserRoleWhere`, `middleware/auth.ts:95-100`).
- Platform admin auth is a fully separate identity + middleware chain (`modules/platform/platform-auth*.ts`, `middleware/platformAuth.ts`).

### tenancy / org isolation
- Tenant root = `Organization` (uuid, slug unique, status, soft-delete `deletedAt`, per-org AI defaults + BYOK keys encrypted, `schema.prisma:12-64`). Every domain table carries `orgId` (or reaches it via agent). There is **no Postgres RLS** — isolation is entirely query-layer discipline, guarded by an e2e suite (`__e2e__/tenant-isolation.e2e.test.ts`).
- Org-level feature flags live in `Organization.settings` JSONB and gate routes via `requireOrgFeature` (`middleware/orgFeature.ts:6-24`; resolution order documented at `schema.prisma:1776-1778`: org override → PlanFeature.enabled → catalog default).
- Suspension kill-switch enforced at login, refresh, authenticate, webhook gate, and chat (`assertOrgActive`, `chat.service.ts:861`).

### agents CRUD + config
- `modules/agents/agent.service.ts`: `createAgent` enforces subscription agentLimit inside a transaction creating Agent + AgentConfig (defaulting `compliance.voice.customLlm:true`) + an `AgentIntegration(platform='elevenlabs')` with generated apiKey/signingSecret, then best-effort syncs the remote ElevenLabs agent (`agent.service.ts:235-296`). Reads/writes are org-scoped (`getAgents(orgId)` etc., lines 302-381).
- `AgentConfig` (1:1) holds model/provider/systemPrompt/personality/appearance JSONB, compliance JSONB (rating/transcript/disclosure/voice.customLlm), vision settings, BYOK `apiKeyEncrypted`, voice fields (`schema.prisma:236-263`).
- Per-agent public surface security = origin allowlist stored in `appearance.allowedOrigins`; missing Origin is rejected when `requireOrigin` (state-changing/expensive public endpoints) — but note localhost origins are dev-only-gated (`agent-origin.service.ts:9-19,58-82`).

### channels / WhatsApp & messaging integrations
Two generations run side by side:
- **Legacy** (`modules/integrations/webhook.routes.ts`, header comment marks it legacy since the 2026-05-24 overhaul): per-agent URLs `/api/webhooks/{telegram|whatsapp|http|email|elevenlabs}/:agentId`. WhatsApp GET does hub.verify_token challenge against per-integration credential or global config fallback (`webhook.routes.ts:513-538`); POST acks 200 immediately, normalizes, gates via `loadActiveIntegration` (integration active + agent active + org active + org features `integrations` and `integration.{platform}`, lines 303-336), marks read, handles `/start`,`/reset`, then calls `processMessage` and sends the reply via Graph API (`sendWhatsAppReply`). Telegram includes voice-note STT/TTS via ElevenLabs.
- **V2** (`webhook-v2.routes.ts` + `services/integrations/core/*` + one file per provider under `providers/`): URL `/api/webhooks/:provider/:channelId`. Flow: early-200 ack → per-channel in-memory rate limit (`core/rate-limiter.ts`) → rawBody signature verification via provider (`whatsapp.provider.ts:132-139` uses Meta `x-hub-signature-256` with app secret) → normalize → `dispatchInbound` (`core/inbound-pipeline.ts:12-89`) which honors inbound STOP/opt-out keywords into the suppression list, resolves media (WhatsApp media id downloaded & re-hosted to S3, `providers/whatsapp.provider.ts:181-199`), then feeds `processMessage` and replies via `outbound-dispatcher`.
- Providers registered by side-effect import of `services/integrations/providers` (`index.ts:39`): whatsapp, telegram, slack, facebook-messenger, instagram-dm, x, linkedin-leads, gmail, outlook, microsoft-teams, sms, email-bridge, webhook, webpush, fcm, apns. A platform-wide Meta webhook (one Meta App across FB/IG/WA) mounts at `/api/integrations/webhook/meta` (`app.ts:325-327`, `webhook-meta.routes.ts`).
- OAuth connections: `IntegrationConnection` (+BYOA client credentials encrypted) with `OAuthState` PKCE rows and a token-refresh queue; token vault e2e-tested (`core/token-vault.e2e.test.ts`, `oauth-state.e2e.test.ts`).

### chat / conversation engine
- `modules/chat/chat.routes.ts`: public widget surface (message, stream, close, handoff, widget-messages, rating, export, upload-attachment) each gated by `assertAgentOriginAllowed` + zod body validation + `requireConversationAccess` ownership middleware (routes :79-146); dashboard half switches to `authenticate` mid-router (:149-187) — which is why `identityRoutes` must mount before `chatRoutes` (`app.ts:297-300`).
- `resolveConversationId` (`chat.service.ts:1015-1121`): resume-by-(agent, channel, sender-or-identity), closed→new thread, anonymous→verified **adoption** which permanently closes the thread to anonymous callers (comment at 1100-1110).
- Ownership check returns NotFound (not Forbidden) to avoid existence oracle (`assertConversationOwnership`, 1123-1140).
- Handoff: `requestHumanHandoff` stamps `humanHandoffAt`; while open, AI stays silent (`processMessage` early-return 1521-1529); support staff reply as role `human` from the inbox (`modules/support/support.service.ts:75-100`) and forwards to the originating channel via `integration-messaging.service`.

### prompt & personality layer
- `services/ai/personalityPrompt.ts` (455 lines) renders tone/language/customInstructions into the system prompt; compliance JSONB injects disclosure strings, restricted-topics and refusal rules — both unit-tested including a dedicated compliance test (`personalityPrompt.compliance.test.ts`).
- `buildSystemMessage` also stamps the real current date/time ("give the assistant the real current date and time", commit f829674), channel hints, vision instructions when enabled, acting-user personalization for verified identities (`actingUserPrompt.test.ts` covers roles/timezone/share claims rendering from `identity.service.ts:300-334`).
- Rolling memory: once history outgrows the live window, older turns fold into `Conversation.memorySummary` tracked by `memorySummarizedCount` so only new backlog is re-summarized (`schema.prisma:475-481`, `services/ai/memory.ts`). Durable cross-conversation facts merge into `ExternalIdentity.memory` **only** for verified identities (`analysis.worker.ts:209-224`).

### safety screening layer
- `services/ai/safetyScreening.ts`: `computeScreening` (chat.service.ts:1348) classifies the user turn via LLM when org config enables it; `applySafetyScreening` (1404) acts on verdicts — `containment` returns transcript-only response, `handoff` triggers human escalation, `flag`/`none` fall through. Deliberately invoked *inside* processMessage/processMessageStream so every entry point (widget, webhook, voice, playground) gets it, not just two routes (comment at chat.routes.ts:75-78).
- Custom HTTP actions are risk-tiered behind a deterministic confirmation gate: high-risk actions require an explicit approval reply intercepted before the LLM runs (`resolveActionConfirmationFromReply` at chat.service.ts:1557-1568, `services/ai/customActions.ts`, "risk-tier custom actions behind a confirmation gate" commit 129ea16). Every resolved action URL passes the SSRF guard at call time (schema comment 383-388, `services/security/urlGuard.ts`).

### LLM / AI layer
- Provider routing is real multi-provider: gemini/openai/anthropic specs with model-id shape checks, SystemConfig default models, per-provider key fallbacks, reasoning-model temperature quirk handling (`services/ai/modelProvider.ts:20-145`). Resolution order: agent BYOK key → org default key → platform SystemConfig key (`services/ai/resolveWorkspaceAi.ts:26-49`).
- Prompt assembly: `buildSystemMessage` (`chat.service.ts:188`) concatenates personality/compliance/grounding/memory/integration context — deliberately plain-string (LangChain template braces incident documented at 1142-1152). RAG context wrapped in escaped `<DOC>` tags with `KB_TRUST_GUARD` anti-injection instruction and `[ESCALATE_TO_HUMAN]` marker stripping (`services/ai/rag.ts:28-76`); tool outputs wrapped by `wrapToolOutput` with a `TOOL_OUTPUT_TRUST_GUARD` injected into the system prompt inside `runToolLoop` (`chat.service.ts:310,441-450`).
- Streaming: SSE from controller (`chat.controller.ts:48-88`); `streamMarkerFilter` strips internal markers from token stream; `runToolLoop` streams per iteration with fresh `AbortSignal.timeout(llmTimeout)`, falls back to non-streamed invoke on first-chunk crash, retries empty STOP completions twice with a nudge, prunes oversized tool messages (`pruneToolMessages`, 24000-char cap), and accumulates usage across iterations for billing (`chat.service.ts:422-683`).
- Quotas: `assertMessageQuota` counts user messages over a rolling 1-month window vs Subscription.messageLimit with Redis-deduped 70%/90% alerts (`chat.service.ts:867-923`); `assertVoiceQuota` analogous for voice minutes (924-1014).
- History: `loadChatHistory` caps the live window (CHAT_HISTORY_LIMIT=20, mirrored by voice's `VOICE_HISTORY_LIMIT` at voiceLlm.routes.ts:62) and re-hydrates image attachments for vision-enabled agents (`visionHistoryOptsFromConfig`, 684; per-index image allocation 711). Tool-message pruning keeps any single tool result ≤24k chars in-context (`pruneToolMessages`, 381).
- Failure laddering on empty model output, each fallback answering a *specific* known-empty case before a generic one: generated-file present → `fileReadyFallback`; tool calls present → last successful tool result; pending Odoo confirmation → `resolveOdooConfirmationFromReply`; else `EMPTY_RESPONSE_FALLBACK` (chat.service.ts:1728-1760).

### knowledge / RAG
- Ingestion: sources of type file/url/text/faq/crawler; upload goes to S3 (`utils/s3.ts`), then `addKnowledgeJob` → `knowledge.worker.ts`: extract (pdf-parse / mammoth DOCX→HTML→Markdown / cheerio HTML / text, `knowledge.worker.ts:32-80`), safeFetch for URLs (`services/security/urlGuard.ts` SSRF guard), structural Markdown chunking with section breadcrumbs (`services/knowledge/chunker.ts`), optional LLM contextual enrichment (`enrich.ts`), batched embeddings (8 in flight, `indexer.ts:69-88`), atomic chunk swap in one transaction (`indexer.ts:90-108`), optional cross-source conflict detection (`ai/knowledgeConflict.ts`), optional ElevenLabs KB sync.
- Crawls: `KnowledgeSource.config` holds maxDepth/maxPages/schedule/patterns/renderMode ('static'|'auto'|'browser' via puppeteer); `KnowledgePage` is the unit of change detection (contentHash skip); `KnowledgeSyncRun` audits each run; differential recrawls driven by `nextSyncAt`/`syncIntervalHours` + `knowledge-sync` queue sweeper (`jobs/workers/knowledgeSync.worker.ts`, schema 265-354).
- Retrieval: query embedding with `RETRIEVAL_QUERY` task type → `hybridSearch`: three SQL CTEs (pgvector cosine dense LIMIT 40, tsvector 'simple', tsvector 'arabic') fused by Reciprocal Rank Fusion k=60, all arms join-scoped to `agent_id AND status='ready'` (`services/knowledge/retrieval.ts:37-115`) → optional rerank (`reranker.ts`, provider from KNOWLEDGE_RERANKER env) → ±1 (±2 for multi-question queries) neighbor expansion (`retrieval.ts:129-171`, multi-part heuristic `rag.ts:104-106`).
- Self-improvement: analysis worker mines FAQ/gap suggestions into `KnowledgeSuggestion` deduped by normalized questionKey (`analysis.worker.ts:184-207`, `suggestions.service.ts`).
- Embeddings service: Gemini-only REST call pinning `outputDimensionality=1536`, transient-error retry w/ jittered backoff, circuit breaker keyed by provider+API-key-hash so one tenant's 429 doesn't open the breaker for everyone (`services/ai/embeddings.ts:20-238`).

### voice / ElevenLabs
- Widget voice: signed-url / conversation-token exchange (`agent.service.ts:27-70`), transcript import on /stop (`widget.routes.ts` import + `voiceTranscript.ts`), post-call webhook with HMAC (`postCallWebhook.routes.ts`).
- **Custom LLM path** (this branch's namesake): `POST /api/voice-llm/...` implements the OpenAI-chat-completions-compatible contract ElevenLabs calls per turn; reuses the exact text-chat brain (RAG, MCP/Odoo bundles, safety screening, tool loop) with tighter budgets — 6 iterations, 12s tool timeout, 12s LLM timeout (`voiceLlm.routes.ts:62-78`, header comment 1-27). Auth is per-agent API key + signing secret via `loadActiveIntegration(agentId,'elevenlabs')` with constant-time compares (`timingSafeEqualStrings`, 55-60).
- Native MCP tool server for voice agents (booking/handoff tools) mounted at `/api/mcp/elevenlabs` authenticated per-agent API key (`services/elevenlabs/mcpServer.routes.ts`, `voiceMcp.ts`).

### external identity (Odoo SSO into chat)
- Assertion exchange: `POST /api/chat/:agentId/identity/exchange` (origin-checked) → provider verify (JWS from Odoo addon) → upsert ExternalIdentity → mint 32-byte opaque token storing only SHA-256 hash; replay defence = UNIQUE `assertionJti` (`<installationId>:<jti>`) claimed by the insert itself (`services/identity/identity.service.ts:63-195`, P2002 → audit + reject).
- Session resolution returns a trusted context derived wholly from our DB; revoked/expired session or revoked identity ⇒ null; bound to the issuing agent (`identity.service.ts:205-248`).
- Durable per-person `memory` JSONB with retention purge worker + RTBF endpoint (`purgeExpiredMemory` 460-492, `purgeIdentityMemoryNow` 504-518, worker `jobs/workers/identityMemoryRetention.worker.ts`).
- Delegation keys (per-user Odoo execution credentials) AES-encrypted on the session, used to prove possession for per-operation grants (`DelegationInput` 55-61, `loadDelegation` 380-406).

### odoo / dynatrace / splunk (native enterprise connectors)
- Odoo: org-level `OdooConnection` (JSON-2/jsonrpc auto-detect, discovered env snapshot, addon HMAC secret with rotation grace window, identityMode service|end_user) + per-agent `AgentOdooConnection` with deny-by-default op classes (read always-on; capture/normal/financial/lifecycle/batch writes individually granted; accessMode internal_only default) (`schema.prisma:760-878`). Writes flow through a durable ledger `OdooOperation` with idempotencyKey, payloadHash re-check on approval, state machine pending→approved→executed/reconciled (`schema.prisma:886-948`, `services/odoo/operationLedger.ts`, executor + worker `odooOperations.worker.ts`); dedicated minimal audit trail `OdooAuditEvent` (955-986). Docs: `docs/odoo/{architecture,policy,migration,threat-model}.md`.
- End-user execution: in `identityMode:'end_user'` the Botify Odoo addon executes tool calls via `with_user()` so *Odoo's own* ACLs/record-rules/company scoping decide outcomes; reads degrade to fields the acting user may see (commit 38d0d34); the per-session delegation key proves possession for per-operation grants (`services/odoo/grant.ts`, `endUserExecution.test.ts`, `odooAddonClient.ts`). Tenant model policy overlay lets operators classify their own custom/Studio models that the hash-pinned global manifest cannot know (`policy/tenantModels.ts`, schema comment 784-796).
- Shared capability framework: `capabilityRegistry.ts` (per-provider feature detection), `accessPolicy.ts` (who may see which tools given accessMode + identity), `evidence.ts` (structured extraction of results for ReportArtifacts), `evaluationSuites.ts` — introduced by the "integrations: shared capability/policy/evidence framework" commit e295587 and adopted by odoo/dynatrace/splunk commits cdab0c1/3489105/8d76b83.
- Dynatrace: read-only Env API v2 tools + Grail DQL via optional Platform token; per-agent allowedTools/defaultScope and opt-in workflow allowlist double-checked at call time (`schema.prisma:992-1059`, services/dynatrace/*). Hard-won lessons encoded as fixes: classic Events API retirement fallback to DQL (113d3d0), forecast execute-path pulled then re-landed on the real Davis Analyzers path (0b231ea→400b9bd), scope-aware gating with self-healing stale-scope windows (323168a).
- Splunk: read-only SOC triage mirroring dynatrace; SPL free-form is re-enforced against `allowedIndexes` at call time, backtick-bypass and cross-connection circuit collisions patched (1061b33) (`schema.prisma:1064-1110`).
- All three share the capability/evidence/access-policy framework in `services/integrations/{capabilityRegistry,accessPolicy,evidence}.ts` and expose `accessMode` publication boundary (origin never authentication — comment at schema.prisma:1098).

### MCP (model context protocol)
- Org-level `McpServer` registry (transport http, authType none|header|bearer|oauth2_cc, secrets AES-encrypted, cached OAuth client-credentials tokens) × per-agent `AgentMcpServer` allowedTools (`schema.prisma:709-756`). Cached clients + header encryption in `services/mcp/client.ts`, `mcpAuth.ts`. Tools merged into the chat loop alongside native bundles (`chat.service.ts loadChatResources`).
- Client hardening unit-tested: auth-header injection (`client.authHeaders.test.ts`) and result deduplication (`client.dedupe.test.ts`). Tool schemas are pre-converted to Gemini-safe declarations before `bindTools` — LangChain's own converter emits JSON-Schema keywords Gemini 400s on, killing whole turns (`geminiToolSchema.ts`, comment at chat.service.ts:427-430; prod incident commit 2684c25).

### widget client (embeddable frontend)
- Paths: `packages/widget/src/{main.ts,core/*,voice-entry.ts}`; built as a framework-free IIFE via Vite (`vite.config.ts`) with a separate voice bundle (`vite.voice.config.ts`).
- Entry: the embed `<script data-agent-id data-api-url>` mounts `ChatWidget` into a Shadow DOM root (style isolation), exposes `window.Shamsi` and replays pending `postMessage` preview overrides (`main.ts:3-15`). Config (colors/texts/locale/compliance banner/voice flags) comes from `GET /api/widget/:agentId` which whitelists and clamps every field server-side — hex colors regex-checked, strings length-capped, URLs protocol-validated before reaching the client (`widget.routes.ts:31-120`).
- Chat transport: SSE `/stream` with fallback to POST `/message`; markdown rendering sanitized locally (`core/widget-markdown.ts`, markup builder `widget-message-markup.ts`); conversation resume via localStorage + identity token header when verified.
- Voice: ElevenLabs WebRTC via signed-url/conversational-token endpoints; transcript imported to the platform conversation on /stop (`services/elevenlabs/voiceTranscript.ts`), voice-minute quota checked server-side (`assertVoiceQuota`).

### transcript & crawler services
- Transcript export renders txt/json/pdf (pdfkit) with compliance gating (`services/transcript/transcriptExport.ts`, `chat.service.ts:2521`); size-bounded and origin-checked on the public route (`chat.routes.ts:127-133`).
- Crawler: `services/crawler/` drives URL sources — static fetch by default, puppeteer browser rendering when `renderMode:'browser'` or auto-detected SPA behavior; per-page politeness via safeFetch (SSRF-guarded, response-size/type caps hardened in commit 4a98dde "slow/huge/wrong-type responses").

### booking (demo scheduler)
- Platform-owned single-row settings (`DemoBookingSettings` id="default", availability JSON array of weekly rules, fixed UTC offset — Gulf no-DST rationale at `schema.prisma:200-203`). Public slot listing + confirm create `DemoAppointment`, send owner/customer emails (`modules/booking/booking.service.ts:81-120`, `booking.public.routes.ts`). Admin surface rides on platform routes.

### artifacts / files / reports
- Chat-generated files: unified `create_file` tool producing CSV/XLSX/PDF/DOCX (`services/ai/fileTools.ts`, 1252 lines) delivered as message attachments with a no-text fallback (`chat.service.ts:1728-1731`). Generation is hard-gated on explicit user intent (commit a25053a) so the model doesn't spontaneously produce downloads; a silent model with files ready still delivers via `fileReadyFallback`.
- Standalone upload/download surface for dashboards at `/api/files` (`files.routes.ts`) against S3/MinIO (`utils/s3.ts`); private media served through HMAC-signed short-lived URLs keyed off ENCRYPTION_KEY (README:63).
- ReportArtifacts: revisionable Excel/Word reports generated from conversations during Odoo/Dynatrace/Splunk investigations; object key + spec/provenance stored **encrypted**, client gets short-lived capability token hashed at rest; revisions linked via self-relation (`schema.prisma:610-657`, `modules/artifacts/artifact.routes.ts` + test). Evidence extraction feeding these comes from the integrations `evidence.ts` framework — every observed tool result during `runToolLoop` is recorded via the `onToolResult` callback (`chat.service.ts:1669-1671`).

### outreach / Campaign Manager
- Models: ContactList→OutreachContact (raw columns preserved verbatim, AI enrichment, dedupeKey, audienceType cold|engaged), Campaign (goalType/budget/channels/messageBrief/ratePerHour/quietHours/requireApproval), CampaignRecipient (per-recipient generated content + engagement timestamps), Segment (rule DSL), CampaignVariant (A/B), Journey/JourneyRun (node DAG engine), TrackedLink, SuppressionEntry, MarketingConsent, ChannelHealth (warmup + kill-switch), EmailSendingDomain (SPF/DKIM/DMARC), WhatsAppTemplate (`schema.prisma:1291-1710`).
- Send safety spine in `services/outreach/safety/*`: suppression hard gate, consent basis check, content screening, warmup caps, channel health pause. Five dedicated queues + journey tick; send orchestrator self-rate-limits by chaining delayed jobs (`addOutreachSendJob` comment, `queue.ts:61-71`).
- Feature-flagged per org (`outreach.campaigns`, autopilot flag noted in schema comment 1386-1388).

### social publishing & push
- SocialAccount/SocialPost/SocialPostTarget for organic publishing to FB Page/IG/LinkedIn/X via OAuth'd connections; repeatable scan promotes due posts, metrics sweep every 6h (`queue.ts:83-93`, `social.worker.ts`).
- Push: PushSubscriber (web/FCM/APNs, endpointHash uniqueness) + PushDelivery per device; public collector endpoints any-origin (`app.ts:179-185`); VAPID/service-account creds reuse IntegrationConnection plumbing (schema comment 1793-1797).

### analytics / quality analysis
- Async per-conversation analysis (BullMQ, 3s delay, 4 attempts, 70s fixed backoff for Gemini 429) producing satisfaction/sentiment/lead/issues/QA sub-scores/frustration/churn + suggested FAQ (`jobs/workers/analysis.worker.ts:15-237`). The worker always calls `gemini-2.5-flash-lite` directly regardless of tenant chat provider — BYOK non-Gemini keys are deliberately ignored here to avoid 401s (comment 85-93). A backfill sweeper re-analyzes closed conversations that never got analyzed (`startAnalysisBackfillWorker`, `jobs/conversationTimeout.ts`).
- Alert rules/lock/metrics in `services/alerts/*` monitored by `alertMonitor.worker.ts` (quality-alert resolution flow: `ConversationAnalysis.qualityAlertResolvedAt/ById/Note` fields, schema 680-682).
- Tenant dashboards aggregate via `modules/analytics/analytics.routes.ts` (9 routes under `/api/agents/:agentId`); platform-wide roll-ups in `modules/platform/platform-analytics.*`. Conversation tags (GIN-indexed String[]) and rating fields power list filtering (`schema.prisma:471-474,496`). Runtime ops metrics (queue depth, per-route latency, 5xx counts) exposed unauthenticated at `/api/metrics` (`app.ts:240-277`).

### ai-studio & notifications
- `/api/ai` (ai-studio): campaign draft generation, content/ad writing, prediction, insights — LLM utilities behind JWT for the marketing suite (`app.ts:349-350` comment, `modules/ai-studio/ai.routes.ts`).
- Notifications: in-app rows created by `services/notifications` (quota alerts deduped via Redis keys `quota_alert:{org}:{period}:{kind}:{threshold}`, chat.service.ts:899-907), realtime push to user rooms, email fallback; web-push delivery path handled separately by the push module.

### notifications & audit logs
- In-app Notification rows + Socket.IO `notification:new` to user rooms (`emitUserNotification`, conversationRealtime.ts:140-156); email via Resend/Nodemailer (`services/email`); web-push delivery.
- `AuditLog` with orgId scope for tenant-readable trails (`schema.prisma:1152-1171`), written by `logAudit` across identity/Odoo/GDPR flows; retention swept by `auditRetention.worker.ts`. Separate OdooAuditEvent table for that connector.

### billing / plans / quotas
- Dynamic catalog editable from platform-admin: Plan / FeatureCatalog / PlanFeature cached in-process and hot-reloaded (`services/plans/planCatalog.ts`, schema comments 1712-1717). Subscription denormalizes limits (-1 = unlimited) with `currentPeriodEnd`; rolling-period quota workers: `jobs/subscriptionPeriod.ts`. PricingConfig/OrgBillingSettings track per-unit price + markup + outstanding balance for manual invoicing (`schema.prisma:1173-1204`).
- No payment gateway in code — billing is operator-managed (platform-billing.controller adjusts balances).

### consent / compliance / GDPR
- Widget GDPR consent ledger `ConsentRecord` (policyVersion, IP/UA) from banner/public endpoint (`schema.prisma:410-428`, `organizations/consent.routes.ts`).
- Right-to-access export capped at 5000 conversations excluding secrets/vectors; RTBF flows for identity memory (`gdpr.service.ts:1-40`, identity RTBF above). Compliance JSONB on AgentConfig gates public rating/transcript-export/disclosure server-side (`chat.routes.ts:115-133` comments FR-26/FR-27).

## FLOWS

### 1) Inbound WhatsApp (v2) → reply
1. Meta POSTs `/api/webhooks/whatsapp/:channelId`; no `Origin` header so CORS passes; `express.json` stashes rawBody because the path matches `/api/webhooks/` (`app.ts:196-204`).
2. Router acks 200 immediately to stop Meta retrying (`webhook-v2.routes.ts:38-39`), then loads channel + connection via `loadActiveChannel` (`core/channel-gate.ts`) — inactive channel ⇒ silent drop after the ack.
3. Per-channel in-memory rate check; excess dropped with a warn log (`webhook-v2.routes.ts:50-56`, `core/rate-limiter.ts`).
4. Signature verification: `x-hub-signature-256` HMAC-SHA256 using the Meta app secret resolved from platform config or BYOA connection (`providers/whatsapp.provider.ts:132-139` → `core/signature.ts`); missing rawBody or bad sig aborts.
5. `normalize()` walks entry/changes/messages into `NormalizedInbound[]`: text bodies, and media messages become `{providerRef: mediaId}` attachments (`whatsapp.provider.ts:141-178`).
6. `dispatchInbound` (`core/inbound-pipeline.ts:12-89`): inbound STOP/إلغاء keywords add a `SuppressionEntry` and return (no AI, no reply); image attachments are downloaded from Graph and re-hosted to S3 via `media.resolve` (`providers/whatsapp.provider.ts:181-199`); non-image media becomes a bracketed note in the text.
7. `processMessage(agentId, {channel:'whatsapp', externalUserId})` (`chat.service.ts:1477-1812`): load agent+config+org → `assertOrgActive` → `resolveWorkspaceAi` (BYOK chain) → `assertMessageQuota` (rolling-month COUNT vs subscription) → `resolveConversationId` resume-by-sender → optional `computeScreening` LLM safety pass → **DB write #1** user Message → handoff short-circuit → safety containment/handoff outcomes → deterministic confirmation interceptors for pending custom-actions/Odoo writes → `loadChatResources` runs RAG retrieval *and* all tool-bundle builds concurrently (`chat.service.ts:1199`) → `runToolLoop` drives model↔tools (each tool call wrapped by `invokeToolWithTimeout`, DB-free) → marker stripping + empty-response laddering.
8. **DB write #2** assistant Message (with metadata.toolCalls/tokenUsage/aiModel); `emitConversationMessage` fans out to the Socket.IO room on every persisted message (`conversationRealtime.ts:128-138`).
9. Reply leaves via `sendToChannel` → provider `outbound.send` → Graph API `{phoneNumberId}/messages`, split at 4000 chars (`providers/whatsapp.provider.ts:202-225`); `AgentChannel.lastInboundAt` bumped (`inbound-pipeline.ts:71-74`).
10. Later, conversation close enqueues `conversation-analysis` (3s delay, 4 attempts, 70s fixed backoff for Gemini 429s — `queue.ts:133-143`); the worker upserts `ConversationAnalysis`, mines `KnowledgeSuggestion`s, merges verified-identity customer memory (`analysis.worker.ts`).

Legacy per-agent WA path differs only in steps 2-5 (`webhook.routes.ts:540-604`) — and currently performs **no POST signature verification** (see RISKS).

### 2) Agent creation/config
1. Dashboard → `POST /api/agents` (`authenticate` + `authorize('agents:create')` on agent.routes.ts).
2. `createAgent` (`agent.service.ts:235-296`): subscription `agentLimit` check (−1 = unlimited) inside a transaction creating Agent(`status:'active'`) + AgentConfig with `compliance.voice.customLlm:true` default + an `AgentIntegration(platform='elevenlabs')` seeded with random apiKey/signingSecret and webhookUrl pointed at the legacy `/api/webhooks/elevenlabs/:id` receiver.
3. Post-commit, best-effort `syncElevenLabsAgentFromLocal(agent.id)` provisions the remote ElevenLabs agent using the ORG's key first (comment 253-256 — platform-key-only provisioning previously put org-key tenants on the wrong ElevenLabs account); failure only logs.
4. Config edits: `PATCH` via `agent-config.service.ts` validated by zod (`agent-config.schemas.ts`); appearance.allowedOrigins changes immediately re-scope the public CORS/origin gate on the next request (no cache).
5. Voice settings propagate outward through `agentConfigSync.ts`, which also wires/unwires the custom-LLM URL and falls back to legacy mode when prerequisites (public webhook base, provisioned secret) are missing (`voiceLlm.routes.ts:5-10`, `agentConfigSync.customLlm.test.ts`).

### 3) Knowledge ingestion → retrieval
Upload → `POST /api/agents/:agentId/knowledge` (zod `knowledge.schemas.ts`) → S3 put + KnowledgeSource(pending) → `addKnowledgeJob` (`queue.ts:33-43`) → worker: extract→chunkMarkdown (section-path aware)→optional enrich→embed batches of 8 (BYOK-key-scoped breaker)→atomic DELETE+INSERT swap→status ready + contentHash (`indexer.ts:40-116`)→conflict detection→optional ElevenLabs sync. Scheduled recrawl: `knowledgeSyncQueue` sweeper picks due `nextSyncAt` sources, per-page hash diff via `KnowledgePage`. Query time: `searchKnowledgeBase` (`rag.ts:108-143`) embed query (RETRIEVAL_QUERY) → hybridSearch RRF → rerank (topK+3 when multi-part) → neighbor expansion → wrapped in escaped DOC tags into system prompt.

### 4) Booking flow
1. Visitor opens the marketing demo page (`(marketing)/[locale]/...` → `PublicBookingPage` screen).
2. `GET /api/booking/...` public route computes bookable slots: `DemoBookingSettings` availability rules (weekday + HH:MM windows) expanded at `slotMinutes` granularity minus buffer, minus existing confirmed `DemoAppointment`s overlapping, rendered in the fixed `utcOffsetMin` (`booking.service.ts:33-61` slot math; rationale "Gulf/Mid-East have no DST" at schema.prisma:200-203).
3. `POST` confirm validates the slot is still free inside a settings-scoped check, creates `DemoAppointment(status='confirmed')`, emails customer + owner via `sendAppointmentCustomerEmail/sendAppointmentOwnerEmail` (`booking.service.ts:1-4` import).
4. Cancellation flips status to `cancelled`; platform admins edit settings and list upcoming/all appointments through `/api/platform/booking/*` (4 routes, platform.routes.ts decomposition above).

### 5) Auth/login session issuance
1. `POST /api/auth/login` passes global limiter → `loginLimiter` (15/15min, Redis store, env-overridable for high-NAT — rateLimiter.ts:85-100).
2. Per-account lockout check: Redis counter `login-fail:{email}` vs configurable max (10) with in-process Map fallback on Redis failure — fail-closed by design (`auth.service.ts:23-72`).
3. User+org+non-expired-roles fetched in one query (email OR phone); bcrypt(12) compare; failure increments the lockout counter; success clears it (`auth.service.ts:357-397`).
4. Gates: unverified email → EMAIL_NOT_VERIFIED; suspended org → ORG_SUSPENDED (403 code the web client force-logs-out on, api.ts:31-36).
5. `createAuthResponse` signs access JWT (15m; claims userId/orgId/email/isOrgOwner/tv) + refresh JWT (7d, userId only), stores refresh single-copy at Redis `refresh:{userId}` EX 7d (`auth.service.ts:97-144`). Rotation on every `/api/auth/refresh`; mismatched stored token ⇒ reject.
6. Every authenticated request re-validates tv/disabled/deleted/suspended against the DB (`middleware/auth.ts:43-70`) — a stolen pre-reset access token dies at next request after `tokenVersion++`.
7. Web client: access token lives in Zustand (`stores/authStore.ts`), axios interceptor attaches Bearer, and on 401 retries once through cookie-authenticated `/api/auth/refresh` (withCredentials) while explicitly excluding public auth endpoints to avoid refresh loops; `ORG_SUSPENDED` triggers logout + toast + redirect (`web/src/services/api.ts:21-60`).

### 6) Org onboarding (register)
1. `POST /api/auth/register` → single transaction (`auth.service.ts:159-264`): Organization (slugified name + uuid suffix, `settings` seeded from `defaultNewOrganizationSettings()` incl. `keyProvisioning` tracker marked pending for gemini/elevenlabs) → User (`isOrgOwner`, 6-digit verification code, 1h expiry) → Owner Role with ALL_PERMISSIONS + UserRole → remaining DEFAULT_ROLES seeded from shared constants → free Subscription (2 agents / 1000 messages / 100MB).
2. Verification email sent best-effort outside the transaction (failure logged, not fatal).
3. `POST /api/auth/verify-email` matches code, flips `emailVerified`, re-seeds default roles idempotently (`ensureDefaultRoles`) and issues first tokens.
4. Teammates join via Redis-stored invite tokens (`invite:{token}` JSON {orgId,email,roleId}) consumed atomically by `acceptInvite` which deletes the key after use (`auth.service.ts:506-600`).
5. Platform-side alternative bootstrap: `POST /api/platform/install` gated by `PLATFORM_INSTALL_TOKEN` creates the first PlatformAdmin (README:93, `.env.example`).

### 7) Human handoff (discovered flow)
Trigger: user asks / `[ESCALATE_TO_HUMAN]` marker (stripped from KB chunks so RAG can't plant it, `rag.ts:24-26`) / safety verdict handoff / widget button → `requestHumanHandoff` stamps conversation → inbox lists open handoffs (`support.service.ts:10-30`) → staff reply persists role=`human` message + realtime emit + channel forward → resolve stamps `supportResolvedAt`; idle-timeout sweeper closes stale ones (`jobs/conversationTimeout.ts`); post-close analysis grades the whole transcript.

### 8) Voice custom-LLM turn (branch namesake)
ElevenLabs → `POST /api/voice-llm` OpenAI-shaped body (per-turn) → agent API-key auth → map trailing user utterance + ≤20 history msgs (`mapOpenAiMessagesToHistory`, voiceLlm.routes.ts:92-111) → rebuild trusted context via `resolveIdentityBySessionId` → same screening/RAG/tool-loop with 6×12s budgets → SSE deltas with `[DONE]`, internal markers filtered by `streamMarkerFilter`.

### 9) Scheduled knowledge recrawl (discovered flow)
`knowledgeSync.worker.ts` runs a repeatable 'sweep' that scans `KnowledgeSource` where `nextSyncAt <= now AND status='ready'` (indexed `[nextSyncAt,status]`, schema.prisma:304) and enqueues per-source 'sync-source' jobs. Each job re-fetches (static fetch or puppeteer per `renderMode`), diffs page contentHashes against `KnowledgePage`, re-indexes only changed pages, writes a `KnowledgeSyncRun` row with added/updated/removed/skipped counts + duration, and advances `nextSyncAt` by `syncIntervalHours`. Dashboard surfaces this as the "سجل المزامنة" tab (schema comment 335-336).

### 10) Support inbox reply (discovered flow)
Staff opens inbox (`GET /api/agents/:agentId/support/...`, JWT + support perms) → joins Socket.IO room via `join:conversation` which re-checks org membership + inbox permission server-side for staff, or identity-token ownership for guests (`conversationRealtime.ts:60-118`) → reply posts role=`human` message stamped `metadata.source:'support_dashboard'` (`support.service.ts:92-99`) → realtime emit + forward to the customer's original channel via `forwardHumanMessageToIntegration` (`support.service.ts:7-8`) → resolve stamps `supportResolvedAt`; idle sweeper auto-closes; close enqueues analysis.

### 11) Campaign send (Campaign Manager)
1. Contact upload → `POST` list with file → S3 + `ContactList(pending)` → import queue: AI column mapping (`services/outreach/columnMapping.ts`) normalizes into fullName/email/phone/whatsapp/telegram/instagram/facebook while preserving every original column verbatim in `raw`, dedupes via `dedupeKey` (`schema.prisma:1325-1359`).
2. Audience: raw list or Segment rule DSL (`segmentDsl.ts`, JSON `{match, rules[]}` evaluated over contact fields + enrichment; source may be `odoo` for live pulls).
3. Compose queue generates per-recipient subject/body from the campaign brief (A/B split across `CampaignVariant` weights when enabled); recipients move pending→generated→approved.
4. Human approval gate unless org autopilot flag is cleared (`requireApproval` default true).
5. Send orchestrator per recipient checks suppression (hard gate), marketing-consent basis per channel (`safety/consent.ts channelRequiresConsent`), ChannelHealth paused/warmup daily caps, quiet hours — then dispatches through provider outbound and self-rate-limits by enqueueing the next recipient with `delayMs = 3600/ratePerHour` (`queue.ts:61-65` comment "One recipient per job").
6. Engagement: open pixel/click redirect via TrackedLink stamp `CampaignRecipient.openedAt/clickedAt/convertedAt`; inbound STOP keywords anywhere in the flow land in SuppressionEntry via the shared pipeline (`inbound-pipeline.ts:17-37`).

## APIS

All mounts from `app.ts:293-354` with route counts (grep of verb registrations):

| Mount | Router file | Count | Auth |
|---|---|---|---|
| `/api/auth` | auth.routes.ts | 12 | public + limiter; refresh via cookie |
| `/api/agents` | agent.routes.ts | 19 | JWT + permission |
| `/api/agents` (knowledge) | knowledge.routes.ts | 12 | JWT + permission |
| `/api/agents` (actions) | actions.routes.ts | 5 | JWT |
| `/api/chat` (identity first!) | identity.routes.ts | 3 | origin-checked public; assertion IS the credential |
| `/api/chat` | chat.routes.ts | 14 | public half origin-checked; dashboard half JWT |
| `/api/agents` (analytics) | analytics.routes.ts | 9 | JWT |
| `/api/agents` (integrations) | integration.routes.ts | 5 | JWT |
| `/api/integrations/connections` | connections.routes.ts | 5 | JWT |
| `/api/integrations/oauth` | oauth.routes.ts | 8 | JWT + state |
| `/api/integrations/catalog` | catalog.routes.ts | — | JWT |
| `/api/agents/:agentId/channels` | channels.routes.ts | 5 | JWT |
| `/api/org` | org.routes.ts | 7 | JWT |
| `/api/consent` | consent.routes.ts | — | mixed public |
| `/api/roles`, `/api/team` | role/team.routes.ts | 4/4 | JWT admin perms |
| `/api/webhooks` (post-call first) | postCallWebhook.routes.ts | 1 | HMAC signed |
| `/api/webhooks` (legacy) | webhook.routes.ts | 7+generated | per-integration API key (http/email/elevenlabs); **none for telegram/whatsapp POST** |
| `/api/webhooks` (v2) | webhook-v2.routes.ts | 2 | provider signature |
| `/api/voice-llm` | voiceLlm.routes.ts | 1 | agent API key |
| `/api/mcp/elevenlabs` | mcpServer.routes.ts | 3 | agent API key |
| `/api/integrations/webhook/meta` | webhook-meta.routes.ts | 2 | Meta signature |
| `/api/widget` | widget.routes.ts | 3 | origin-checked public |
| `/api/platform` | platform.routes.ts | 101 | PlatformAdmin JWT (+super for some); install token for bootstrap |

The `/api/platform` mount decomposes as: `/agents` ×35 (cross-tenant agent inspection/control), `/orgs` ×16 (suspend/delete/restore/features/impersonation-adjacent controls), `/billing` ×8, `/plans` ×7 + `/features` ×4 (dynamic catalog), `/booking` ×4 (demo scheduler admin), `/system-config` ×2 (hot-reloaded KV), `/mcp-servers` ×2, plus trash/audit-logs/admins/install. Controllers live as `platform-*.controller.ts` siblings in `modules/platform/`.
| `/api/files`, `/api/artifacts`, `/api/mcp`, `/api/odoo`, `/api/dynatrace`, `/api/splunk` | respective | 5/3/11/19/11/11 | JWT |
| `/api/identity` | identity.admin.routes.ts | 3 | JWT org admin (RTBF/retention) |
| `/api/reports` | report.routes.ts | 2 | mixed capability-token |
| `/api/outreach` (public unsubscribe BEFORE auth router) | outreach.public.routes.ts | 4 | token-in-path |
| `/api/push` collector | push.public.routes.ts | 4 | public any-origin |
| `/api/outreach/{segments,journeys,email-domains,push}` | 7/8/5/6 | | JWT |
| `/api/outreach` catch-all | outreach.routes.ts | 26 | JWT |
| `/api/ai` (studio) | ai.routes.ts | 6 | JWT |
| `/api/social` | social.routes.ts | 7 | JWT |
| `/api/notifications` | notification.routes.ts | 4 | JWT |
| `/api/booking` | booking.public.routes.ts | 3 | public |

Validation: zod schemas per module applied via `validateBody` (`middleware/validate.ts`); multer for uploads (4MB images for vision, `chat.routes.ts:21-31`). Error envelope convention: `{ error: { code, message, details? } }` — AppError passthrough, MulterError mapped (413 FILE_TOO_LARGE), ZodError → VALIDATION_ERROR with field details, unknown → generic 500 INTERNAL_ERROR (`middleware/errorHandler.ts:7-57`). SSE errors follow the same envelope inside `data:` events with AppError-only messages (`chat.controller.ts:72-87`).

## DATABASE

- ORM: Prisma 6.19 (`provider postgresql`, extension `vector`, `schema.prisma:1-10`); migrations in `packages/api/prisma/migrations` — **56 entries**, baseline `20260401000000_baseline`, notable: `20260716160000_hot_path_indexes`, `20260731120000_external_identity`, `20260801000000_conversation_memory`, `20260824120000_knowledge_engine_v2` (adds tsv columns implied by hybrid search), plus drift-reconciliation migrations (`20260911000000_reconcile_legacy_schema_drift`; earlier orphan-table cleanup chain `20260521090000_archive_orphan_tables` → `20260521140000_drop_remaining_drift`). Deploy applies them via `prisma migrate deploy` inside deploy.sh, whose migration guard refuses DROP-containing diffs because prod carried orphan tables from an abandoned branch (deploy.sh:9-13); CI uses `db push --skip-generate` (ci.yml step "Prepare test database").
- 60 models. Grouped by domain with tenant column:
  - Core tenancy: organizations (self), users.orgId, platform_admins (no org), roles.orgId, role_permissions, user_roles, notifications.orgId, subscriptions.orgId(unique), plans/feature_catalog/plan_features (global catalog), pricing_configs, org_billing_settings.orgId, system_configs (global KV).
  - Agents: agents.orgId, agent_configs.agentId(unique FK), agent_actions.{agentId,orgId}, consent_records.agentId.
  - Conversational: conversations.agentId (+externalIdentityId nullable), messages.conversationId, conversation_analyses.conversationId(unique), external_identities.orgId, identity_sessions.{externalIdentityId,agentId}, report_artifacts.orgId.
  - Knowledge: knowledge_sources.agentId, knowledge_pages.sourceId (unique [sourceId,url]), knowledge_sync_runs.sourceId, knowledge_suggestions.agentId, document_chunks.sourceId (**embedding vector(1536)** Unsupported type, contentHash, sectionPath, embeddingModel).
  - Channels/integrations: agent_integrations.{agentId,platform} unique, integration_connections.orgId (unique [org,provider,accountId], many `*Enc` token columns + BYOA trio), agent_channels.connectionId+agentId (unique quad, webhookSecretEnc), oauth_states.orgId (state unique), channel_health.orgId.
  - Tool connectors: mcp_servers.orgId + agent_mcp_servers; odoo_connections.orgId (+addonSecretEncrypted, identityMode, tenantModelPolicy) + agent_odoo_connections (op-class booleans) + odoo_operations.orgId (idempotencyKey unique, payloadHash) + odoo_audit_events.orgId; dynatrace_*/splunk_* mirrors.
  - Marketing: contact_lists.orgId → outreach_contacts.listId (unique [listId,dedupeKey]) → campaign_recipients.{campaignId,contactId} unique pair; campaigns.orgId; segments, campaign_variants, journeys → journey_runs (unique [journeyId,contactId]), tracked_links.token unique, suppression_entries unique [orgId,channel,address], marketing_consents same, email_sending_domains, whatsapp_templates.
  - Push/social: push_subscribers.orgId (unique [org,type,endpointHash]) → push_deliveries; social_accounts → social_posts → social_post_targets.
  - Misc: demo_booking_settings (single row id="default"), demo_appointments (no tenant — platform-level), audit_logs.orgId nullable.
- JSONB patterns: capability config blobs (`settings`, `personality`, `appearance`, `compliance`, `config`, `discoveredEnv`, `claims`, `memory`, `graph`, `rules`, `stats`, `importMeta`, `dnsRecords`), encrypted-secret companions stored as TEXT not JSONB, denormalized counters (`stats`, variant tallies).
- Hot indexes: conversations `[agentId,status]`, `[agentId,startedAt]`, GIN on tags, `[agentId,externalIdentityId,status]` (resume lookup), `[voiceCallId]`; messages `[conversationId,createdAt]`; knowledge_sources `[nextSyncAt,status]`, `[syncIntervalHours,status]`; analyses `[qualityAlertResolvedAt]`; outreach `[campaignId,status]`, `[status,scheduledAt]`. HNSW index on document_chunks.embedding created in migration `20260716160000_hot_path_indexes` (README states HNSW; the raw SQL lives in that migration, not the Prisma schema).
- **No RLS anywhere** — isolation relies on Prisma `where` clauses + the e2e suite; org-owner bypass means permission checks are skipped, not scoping.
- **Status-as-string convention everywhere** (`status String @default(...)`) with legal values only in comments — no DB enums or CHECK constraints (e.g. conversations `active/closed`, campaigns `draft|review|scheduled|running|paused|completed|cancelled`, operations state machine). Typos compile; only app logic validates.
- FK delete behaviour worth knowing: org deletion cascades everything tenant-owned (agents, conversations, campaigns…); `Conversation.externalIdentityId` is `SetNull` so RTBF identity revocation keeps transcripts but unlinks them; `Subscription.planRef` SetNull keeps legacy subs alive when a plan row is deleted; ReportArtifact revisions self-reference via `rootArtifactId` SetNull.
- Audit/outbox: audit_logs + odoo_audit_events serve as append-only trails; there is no outbox table — side effects (emails, sends) happen inline or via BullMQ jobs, not transactional outbox.

## TESTS

- Layout: co-located `*.test.ts` beside sources — 153 test files repo-wide, 148 in packages/api alone. Runners: Vitest 4 root devDep; per-workspace `vitest.config.ts` (`include src/**/*.test.ts`, excludes `*.e2e.test.ts` so unit runs stay infra-free — `packages/api/vitest.config.ts`). E2E: `vitest.e2e.config.ts` includes `src/**/*.e2e.test.ts`; needs real DATABASE_URL (+Redis), bootstrapped via `createApp()` + supertest with two seeded tenants (`__e2e__/seed.ts`), asserting zero cross-org leakage on agents/conversations/audit surfaces (`tenant-isolation.e2e.test.ts:1-90`). Additional DB-bound suites live next to core modules (`byoa.e2e.test.ts`, `oauth-state.e2e.test.ts`, `token-vault.e2e.test.ts`, `operationLedger.realpg.test.ts`).
- Coverage of critical flows: strong unit coverage of chat internals (streamMarkerFilter, runToolLoop timeouts/usage, pruneToolMessages, conversation ownership, screening), RAG injection guard (`rag.injection.test.ts`), personality/compliance prompts, embeddings breaker, webhook providers (per-provider signature tests), Odoo policy/isolation/ledger (incl. `operationLedger.realpg.test.ts` against real Postgres), dynatrace/splunk tools, tenant isolation e2e, voice custom-LLM route + agentConfigSync. Periodic sweeps are plain `setInterval` loops (`conversationTimeout.ts:144,226` — conversation idle close + analysis backfill; subscription period rollover in `subscriptionPeriod.ts`) — untested by design but simple.
- Gaps (important code with no direct test found): `modules/support/support.service.ts` reply forwarding, `modules/booking/booking.service.ts` slot math, `jobs/workers/outreachSend.worker.ts` orchestrator and the suppression/consent/quiet-hours gate chain, `services/realtime/conversationRealtime.ts` socket auth, `modules/integrations/webhook-meta.routes.ts`, `services/knowledge/retrieval.ts` fusion math itself (only its callers' behavior is tested via rag tests), widget package has only utils tests (no E2E of script embed). Legacy webhook routes have `webhook.legacy.e2e.test.ts` (partial).
- Commands:
  - all unit tests: `npm test` (turbo across workspaces)
  - single file: `cd packages/api && npx vitest run src/modules/chat/streamMarkerFilter.test.ts` (README:104-106)
  - DB e2e: `docker compose up -d` then `cd packages/api && E2E=1 npx vitest run src/__e2e__/` (header of tenant-isolation.e2e.test.ts)
  - full CI parity: `.github/workflows/ci.yml` quality job = `npm ci` → `npx prisma db push --skip-generate` (packages/api) → `turbo run build lint test` against pgvector/pgvector:pg16 + redis:7 service containers, with CI-only ENCRYPTION_KEY/JWT_SECRET env values.
- Widget/web/platform-admin each carry a `test` script (`vitest run --passWithNoTests`) so turbo's test task never fails on packages without specs.

## GIT LESSONS

From `git log --oneline -60` and `--follow` on hot files:
- **Recurring fix themes**: (1) *Voice/ElevenLabs* — custom-LLM route 404 on every turn ("critical", 49d4d73), IVC/custom_llm conflicts, dead-air hangs bounded, transcript persistence; the branch name itself is this workstream. (2) *Chat robustness* — mid-stream LangChain crashes recovered (c2bb5fb, 437458c), empty completions answered anyway (1852d96), LLM-timeout gap on no-tool turns + SSE leak redaction + token-usage under-counting fixed because it fed real billing (639d06a), iteration-cap guarantees (1694f0d). (3) *Security sweeps* — SSRF-via-redirect (75ce1ad), risk-tiered custom actions (129ea16), timing-safe compares, safety screening moved to the root caller (94f0f86), a 19-finding site review closed wholesale (a648cb3). (4) *Connector churn* — long dynatrace tool-fix chains (forecast pulled then re-landed via Davis Analyzers, Grail metric keys), odoo enterprise ledger/delegation/policy series. (5) *Retrieval tuning* — compound-question blind spot root-caused via live retrieval trace (e6b90e1 → 70e3cf7 budget widening). (6) *Infra gotchas* — nginx compression was simply never on (c25781a); turbo env passthrough silently hides new runtime env vars from CI tasks (README:115); Prisma index-name truncation had to be mapped manually (`schema.prisma:1053-1055`).
- **Fragile/hot areas**: `modules/chat/chat.service.ts` (follow log shows ~30 touches incl. mega-commit ee86115 mixing features), `services/elevenlabs/*`, `services/dynatrace/*`, `services/odoo/*`. Commit style shows single-author (Abd Faraj) with occasional giant squashes — bisectability suffers on those.
- **Branch state**: `master..HEAD` = **47 commits ahead, 0 behind** — master is a strict ancestor; the entire Knowledge Engine v2 + ElevenLabs rebuild + reports/splunk/dynatrace capability framework exists only on this deploy branch. Risk: master-based CI (ci.yml triggers on master) is not testing what ships; any future branch from master silently drops 47 commits' worth of fixes.
- **Dirty state**: exactly one working-tree change — `CLAUDE.md` deleted locally (`git status`). No uncommitted feature/debug/secrets files right now. (A prior examination noted ~157 dirty files; that no longer matches this tree — see UNCERTAIN.) Stray root artifacts exist but are committed/ignored rather than dirty: `fix_widget.js`, `patch_widget.js`, `patch_widget2.js`, `test_chat.ts` (tracked scratch), `graphify-out/`, `artifacts/` (gitignored for containing operational identifiers, `.gitignore:24-27`).

## DECISIONS

- **Zod-at-the-boundary validation** with per-module `*.schemas.ts` and a single `validateBody` middleware; error envelope normalized centrally (`middleware/validate.ts`, `errorHandler.ts`).
- **String permissions + org-owner bypass** instead of bitfield roles (`shared/constants/permissions.ts` ALL_PERMISSIONS, DEFAULT_ROLES); support-inbox access implied by agent-management perms to avoid role sprawl (`middleware/auth.ts:8-19`).
- **Status-as-plain-strings** across all models (no PG enums) — flexible for the operator-driven state machines (campaigns, odoo operations) at the cost of DB-level integrity.
- **AES-256-GCM envelope via ENCRYPTION_KEY** for every tenant secret at rest (org/agent API keys, MCP headers, channel credentials, DKIM private keys, delegation keys), with HMAC-signed private media URLs (README:63, `utils/encryption.ts`).
- **Turborepo+npm workspaces**, shared types package consumed by api/web/widget only (root `package.json`, per-package manifests).
- **Express monolith + separate worker tier** split by `START_WORKERS`, sized for a ~900MB EC2 box (`ecosystem.config.cjs` header; `workers-entry.ts` docstring explains the racing-sweeps rationale).
- **Gemini-first, real multi-provider routing** added later after discovering provider selection was cosmetic (`modelProvider.ts:7-19` docstring); embeddings remain Gemini-only pinned to 1536 dims for pgvector compatibility (`embeddings.ts:1-15`).
- **pgvector hybrid retrieval (dense + simple + arabic, RRF k=60)** because dense-only misses exact lexical signals like SKUs/error codes — decision recorded in `retrieval.ts:1-11`; neighbor expansion chosen over parent-child tables as pragmatic middle ground (`retrieval.ts:122-128`).
- **Verified-identity trust boundary**: `Conversation.externalUserId` documented UNTRUSTED vs `externalIdentityId` VERIFIED; platform claims never an authorization input (`schema.prisma:456-463,504-511`); replay defence via unique jti index rather than application check (`identity.service.ts:47-54`).
- **Deny-by-default Odoo op-class permissions** replacing a single boolean, with documented deliberate security downgrade for financial/lifecycle/batch during migration (`schema.prisma:852-864`, `docs/odoo/migration.md`); durable operation ledger with idempotency replacing in-memory pendingConfirmations (`schema.prisma:880-885`, docs/odoo/architecture.md §3).
- **Custom-LLM voice path default-on** for new agents to reuse the text-chat brain and halve LLM hops, legacy path kept as automatic fallback (`voiceLlm.routes.ts:1-27`, `agent.service.ts:258-266`).
- **DB-backed SystemConfig with Redis pub/sub invalidation** (values never transit pub/sub — keys only, `config.ts:7-12`); mirrored for the plan catalog.
- **Per-key circuit breakers for embeddings** after one tenant's bulk ingest tripped a shared breaker (`embeddings.ts:56-63`).
- **Sync/async boundaries**: chat turns are synchronous HTTP/SSE end-to-end (no queue hop for the reply — webhook handlers call `processMessage` inline after acking, accepting long-lived request work); everything *observational or batch* is queued (analysis, ingestion, sends) or swept on intervals. The one deliberate queue-on-hot-path exception would be none — latency wins over throughput for replies; cost controls are quota checks instead.
- **Early-ack webhook processing** (200 before work) trading at-most-once delivery for Meta retry-friendliness (`webhook-v2.routes.ts:38-39`).
- **Hardened deploy pipeline** with DROP-guard, snapshot, health gate (`deploy.sh` header citing PRODUCTION_READINESS_PLAN.md §4).
- **Shadow-DOM framework-free widget** (single script tag) and Next.js 16 frontends served by PM2 post-migration (`ecosystem.config.cjs` notes the previous nginx-static setup).

## RISKS & TECH DEBT

Ranked, each with evidence:
1. **Legacy webhook forgery (security, high)**: `POST /api/webhooks/whatsapp/:agentId` and `/telegram/:agentId` perform **no signature/secret verification** — anyone who learns or guesses an agentId can inject forged inbound messages that consume LLM spend and send replies (`webhook.routes.ts:540-604` has only `loadActiveIntegration` gating; contrast v2's `verifySignature` at webhook-v2.routes.ts:64-76). Mitigated only by UUID agentIds. Same file's http/email/elevenlabs paths do enforce API keys (616-650).
2. **Dual-running webhook generations (tech debt)**: legacy routes were slated for removal "2 weeks after Phase 2" (comment at webhook.routes.ts:1-8) but remain the default wiring created by `createAgent` (elevenlabs webhookUrl points at the legacy path, agent.service.ts:280-290). Two normalization layers to maintain indefinitely.
3. **At-most-once inbound messaging (reliability)**: ack-before-process means a crash between ack and `dispatchInbound` silently drops customer messages; no DLQ — failed BullMQ jobs are merely trimmed (`removeOnFail {count:500}`, queue.ts:14) with no alerting on accumulation.
4. **No DB-level tenant enforcement (security/architecture)**: zero Postgres RLS; isolation depends on every query remembering orgId/agent joins (acknowledged as the "$47M leak pattern" by their own e2e header, tenant-isolation.e2e.test.ts:1-4). One missed `where` in a new endpoint leaks cross-tenant.
5. **Quota checks are count-then-act (perf/cost)**: `assertMessageQuota` runs a COUNT over messages joined via conversation→agent per message turn (`chat.service.ts:881-889`) — racey under concurrency and O(messages) on the hot path; no pre-paid decrement.
6. **In-memory state assumes single-instance semantics**: channel rate limiter (`checkChannelRate`), embeddings breakers, reranker caches are process-local — behavior diverges across PM2 workers though the Redis adapter made sockets cluster-safe.
7. **CORS reflects no-Origin requests** (`app.ts:160-162` grants `origin:true` when the Origin header is absent) — fine for server-to-server, but combined with `credentials:true` it widens the surface for non-browser tooling; the push collector additionally allows any credentialed-less origin by design (documented).
8. **Anonymous conversation world-writability**: anonymous threads are continuable by anyone presenting the conversationId + matching agent (pre-existing behaviour acknowledged in `assertConversationOwnership`, chat.service.ts:1131-1135); adoption-once-verified mitigates after sign-in.
9. **Deploy branch divergence (process)**: 47 commits on deploy branch unreleased to master (see GIT LESSONS) — CI green on master proves nothing about production.
10. **Scratch/tooling cruft at repo root**: `patch_widget*.js`, `fix_widget.js`, `test_chat.ts`, `query_agent.ts` (in packages/api), `pnpm-lock.yaml` stranded inside platform-admin while the repo is npm-workspaces — confusing fossils for agents and humans alike.
11. **TODO/FIXME scarcity**: only 1 TODO/HACK hit in api non-test code (`providers/microsoft-teams.provider.ts`) — the team encodes debt in long comments instead; those comments are excellent but some files (chat.service.ts 2562 lines, fileTools.ts 1252) are becoming single-maintainer hotspots.
12. **Memory ceilings**: ecosystem.config.cjs explicitly warns the box cannot actually fit all four PM2 apps (~260-400MB added by the Next servers) — ceilings convert OOM into restart loops, they don't add RAM.
13. **Demo booking is unauthenticated** by design (public slots/confirm, booking.public.routes.ts) — spam magnet unless rate-limited upstream; no captcha visible in code.
14. **Unauthenticated ops endpoints**: `/api/metrics` (queue depths, per-route latency, uptime — `app.ts:240-277`) and `/api/openapi.json` + `/api/docs` (`app.ts:281-291`) are mounted before any auth and not rate-limit-exempt; they expose operational topology to anyone who can reach the API.
15. **Dev-only localhost origins are NODE_ENV-gated, not env-gated** (`agent-origin.service.ts:16-18`): if a prod box ever boots without `NODE_ENV=production`, localhost origins become globally trusted origins again. ecosystem.config.cjs sets it today, but nothing else enforces it.
16. **Observability is self-hosted-minimal**: pino logs + Sentry (no-op without DSN, `utils/sentry.ts`) + the hand-rolled `/api/metrics`; no Prometheus/Grafana scrape format, so queue-depth alerts depend on someone reading that JSON.
17. **`console.*` leakage in worker/webhook code**: several hot paths log via bare `console.warn/error` instead of the pino logger (`analysis.worker.ts:96,206,223`, `webhook.routes.ts:231,234`, `agent.service.ts:294`) — inconsistent structured logging loses request context in PM2 log aggregation (root `scripts/logs.sh` greps raw text as a workaround).

## UNCERTAIN

- **Dirty-file history**: the task brief mentioned "~157 dirty files", but `git status --porcelain` at examination time shows exactly 1 (`D CLAUDE.md`). Either the tree was committed/stashed between brief and exam, or the earlier count came from a different machine/moment. Unresolved; current truth is stated in META/GIT LESSONS.
- **HNSW vs IVFFlat**: README asserts "pgvector HNSW" and the hot_path_indexes migration presumably creates it, but I did not open the migration SQL to confirm the index method string; the Prisma schema itself cannot express it (`Unsupported("vector(1536)")`, schema.prisma:434).
- **Knowledge Engine v2 tsv columns**: `hybridSearch` references `dc.tsv_simple` / `dc.tsv_arabic`, which don't appear in `schema.prisma` — they're assumed to be raw-SQL-generated columns from migration `20260824120000_knowledge_engine_v2`; not directly verified.
- **Reranker default**: `rerankChunks` accepts provider config via `KNOWLEDGE_RERANKER`/`KNOWLEDGE_RERANK_PROVIDER` env (turbo.json:13), but whether the default path is a no-op passthrough or calls an external reranker was not traced into `reranker.ts`.
- **Widget markdown sanitization**: README claims "sanitized widget markdown" (`widget-markdown.ts` exists) but I did not audit its XSS posture.
- **Platform-admin ↔ shared divergence**: platform-admin duplicating types/constants instead of importing `@chatagent/shared` appears intentional (no dependency declared) but the reason (bundle size? build isolation?) is undocumented.
- **Prod host details**: `deploy.sh` defaults reveal an EC2 host/IP and PEM path convention; I did not verify which frontend apps are currently enabled in the running PM2 config versus the commented capacity warning in ecosystem.config.cjs.
- Whether the legacy Telegram/WhatsApp signature gap is exploited in practice, or compensated by network-level allowlists (nginx), could not be determined from the repo alone (`infra/nginx/` configs exist but weren't audited for path restrictions).
