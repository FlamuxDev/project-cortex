---
cortex-generated: true
title: chat-agent-saas flows
tags: [flows/project]
---

# chat-agent-saas — Product Flows

End-to-end behaviors as verified from source. Files are the evidence trail.

## 1) Inbound WhatsApp (v2) → reply
*[[chat-agent-saas]] · confidence: inferred*

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

## 2) Agent creation/config
*[[chat-agent-saas]] · confidence: inferred*

1. Dashboard → `POST /api/agents` (`authenticate` + `authorize('agents:create')` on agent.routes.ts).
2. `createAgent` (`agent.service.ts:235-296`): subscription `agentLimit` check (−1 = unlimited) inside a transaction creating Agent(`status:'active'`) + AgentConfig with `compliance.voice.customLlm:true` default + an `AgentIntegration(platform='elevenlabs')` seeded with random apiKey/signingSecret and webhookUrl pointed at the legacy `/api/webhooks/elevenlabs/:id` receiver.
3. Post-commit, best-effort `syncElevenLabsAgentFromLocal(agent.id)` provisions the remote ElevenLabs agent using the ORG's key first (comment 253-256 — platform-key-only provisioning previously put org-key tenants on the wrong ElevenLabs account); failure only logs.
4. Config edits: `PATCH` via `agent-config.service.ts` validated by zod (`agent-config.schemas.ts`); appearance.allowedOrigins changes immediately re-scope the public CORS/origin gate on the next request (no cache).
5. Voice settings propagate outward through `agentConfigSync.ts`, which also wires/unwires the custom-LLM URL and falls back to legacy mode when prerequisites (public webhook base, provisioned secret) are missing (`voiceLlm.routes.ts:5-10`, `agentConfigSync.customLlm.test.ts`).

## 3) Knowledge ingestion → retrieval
*[[chat-agent-saas]] · confidence: inferred*

Upload → `POST /api/agents/:agentId/knowledge` (zod `knowledge.schemas.ts`) → S3 put + KnowledgeSource(pending) → `addKnowledgeJob` (`queue.ts:33-43`) → worker: extract→chunkMarkdown (section-path aware)→optional enrich→embed batches of 8 (BYOK-key-scoped breaker)→atomic DELETE+INSERT swap→status ready + contentHash (`indexer.ts:40-116`)→conflict detection→optional ElevenLabs sync. Scheduled recrawl: `knowledgeSyncQueue` sweeper picks due `nextSyncAt` sources, per-page hash diff via `KnowledgePage`. Query time: `searchKnowledgeBase` (`rag.ts:108-143`) embed query (RETRIEVAL_QUERY) → hybridSearch RRF → rerank (topK+3 when multi-part) → neighbor expansion → wrapped in escaped DOC tags into system prompt.

## 4) Booking flow
*[[chat-agent-saas]] · confidence: inferred*

1. Visitor opens the marketing demo page (`(marketing)/[locale]/...` → `PublicBookingPage` screen).
2. `GET /api/booking/...` public route computes bookable slots: `DemoBookingSettings` availability rules (weekday + HH:MM windows) expanded at `slotMinutes` granularity minus buffer, minus existing confirmed `DemoAppointment`s overlapping, rendered in the fixed `utcOffsetMin` (`booking.service.ts:33-61` slot math; rationale "Gulf/Mid-East have no DST" at schema.prisma:200-203).
3. `POST` confirm validates the slot is still free inside a settings-scoped check, creates `DemoAppointment(status='confirmed')`, emails customer + owner via `sendAppointmentCustomerEmail/sendAppointmentOwnerEmail` (`booking.service.ts:1-4` import).
4. Cancellation flips status to `cancelled`; platform admins edit settings and list upcoming/all appointments through `/api/platform/booking/*` (4 routes, platform.routes.ts decomposition above).

## 5) Auth/login session issuance
*[[chat-agent-saas]] · confidence: inferred*

1. `POST /api/auth/login` passes global limiter → `loginLimiter` (15/15min, Redis store, env-overridable for high-NAT — rateLimiter.ts:85-100).
2. Per-account lockout check: Redis counter `login-fail:{email}` vs configurable max (10) with in-process Map fallback on Redis failure — fail-closed by design (`auth.service.ts:23-72`).
3. User+org+non-expired-roles fetched in one query (email OR phone); bcrypt(12) compare; failure increments the lockout counter; success clears it (`auth.service.ts:357-397`).
4. Gates: unverified email → EMAIL_NOT_VERIFIED; suspended org → ORG_SUSPENDED (403 code the web client force-logs-out on, api.ts:31-36).
5. `createAuthResponse` signs access JWT (15m; claims userId/orgId/email/isOrgOwner/tv) + refresh JWT (7d, userId only), stores refresh single-copy at Redis `refresh:{userId}` EX 7d (`auth.service.ts:97-144`). Rotation on every `/api/auth/refresh`; mismatched stored token ⇒ reject.
6. Every authenticated request re-validates tv/disabled/deleted/suspended against the DB (`middleware/auth.ts:43-70`) — a stolen pre-reset access token dies at next request after `tokenVersion++`.
7. Web client: access token lives in Zustand (`stores/authStore.ts`), axios interceptor attaches Bearer, and on 401 retries once through cookie-authenticated `/api/auth/refresh` (withCredentials) while explicitly excluding public auth endpoints to avoid refresh loops; `ORG_SUSPENDED` triggers logout + toast + redirect (`web/src/services/api.ts:21-60`).

## 6) Org onboarding (register)
*[[chat-agent-saas]] · confidence: inferred*

1. `POST /api/auth/register` → single transaction (`auth.service.ts:159-264`): Organization (slugified name + uuid suffix, `settings` seeded from `defaultNewOrganizationSettings()` incl. `keyProvisioning` tracker marked pending for gemini/elevenlabs) → User (`isOrgOwner`, 6-digit verification code, 1h expiry) → Owner Role with ALL_PERMISSIONS + UserRole → remaining DEFAULT_ROLES seeded from shared constants → free Subscription (2 agents / 1000 messages / 100MB).
2. Verification email sent best-effort outside the transaction (failure logged, not fatal).
3. `POST /api/auth/verify-email` matches code, flips `emailVerified`, re-seeds default roles idempotently (`ensureDefaultRoles`) and issues first tokens.
4. Teammates join via Redis-stored invite tokens (`invite:{token}` JSON {orgId,email,roleId}) consumed atomically by `acceptInvite` which deletes the key after use (`auth.service.ts:506-600`).
5. Platform-side alternative bootstrap: `POST /api/platform/install` gated by `PLATFORM_INSTALL_TOKEN` creates the first PlatformAdmin (README:93, `.env.example`).

## 7) Human handoff (discovered flow)
**Trigger:** user asks / `[ESCALATE_TO_HUMAN]` marker (stripped from KB chunks so RAG can't plant it, `rag.ts:24-26`) / safety verdict handoff / widget button → `requestHumanHandoff` stamps conversation → inbox lists open handoffs (`support.service.ts:10-30`) → staff reply persists role=`human` message + realtim
*[[chat-agent-saas]] · confidence: inferred*

Trigger: user asks / `[ESCALATE_TO_HUMAN]` marker (stripped from KB chunks so RAG can't plant it, `rag.ts:24-26`) / safety verdict handoff / widget button → `requestHumanHandoff` stamps conversation → inbox lists open handoffs (`support.service.ts:10-30`) → staff reply persists role=`human` message + realtime emit + channel forward → resolve stamps `supportResolvedAt`; idle-timeout sweeper closes stale ones (`jobs/conversationTimeout.ts`); post-close analysis grades the whole transcript.

## 8) Voice custom-LLM turn (branch namesake)
*[[chat-agent-saas]] · confidence: inferred*

ElevenLabs → `POST /api/voice-llm` OpenAI-shaped body (per-turn) → agent API-key auth → map trailing user utterance + ≤20 history msgs (`mapOpenAiMessagesToHistory`, voiceLlm.routes.ts:92-111) → rebuild trusted context via `resolveIdentityBySessionId` → same screening/RAG/tool-loop with 6×12s budgets → SSE deltas with `[DONE]`, internal markers filtered by `streamMarkerFilter`.

## 9) Scheduled knowledge recrawl (discovered flow)
*[[chat-agent-saas]] · confidence: inferred*

`knowledgeSync.worker.ts` runs a repeatable 'sweep' that scans `KnowledgeSource` where `nextSyncAt <= now AND status='ready'` (indexed `[nextSyncAt,status]`, schema.prisma:304) and enqueues per-source 'sync-source' jobs. Each job re-fetches (static fetch or puppeteer per `renderMode`), diffs page contentHashes against `KnowledgePage`, re-indexes only changed pages, writes a `KnowledgeSyncRun` row with added/updated/removed/skipped counts + duration, and advances `nextSyncAt` by `syncIntervalHours`. Dashboard surfaces this as the "سجل المزامنة" tab (schema comment 335-336).

## 10) Support inbox reply (discovered flow)
*[[chat-agent-saas]] · confidence: inferred*

Staff opens inbox (`GET /api/agents/:agentId/support/...`, JWT + support perms) → joins Socket.IO room via `join:conversation` which re-checks org membership + inbox permission server-side for staff, or identity-token ownership for guests (`conversationRealtime.ts:60-118`) → reply posts role=`human` message stamped `metadata.source:'support_dashboard'` (`support.service.ts:92-99`) → realtime emit + forward to the customer's original channel via `forwardHumanMessageToIntegration` (`support.service.ts:7-8`) → resolve stamps `supportResolvedAt`; idle sweeper auto-closes; close enqueues analysis.

## 11) Campaign send (Campaign Manager)
*[[chat-agent-saas]] · confidence: inferred*

1. Contact upload → `POST` list with file → S3 + `ContactList(pending)` → import queue: AI column mapping (`services/outreach/columnMapping.ts`) normalizes into fullName/email/phone/whatsapp/telegram/instagram/facebook while preserving every original column verbatim in `raw`, dedupes via `dedupeKey` (`schema.prisma:1325-1359`).
2. Audience: raw list or Segment rule DSL (`segmentDsl.ts`, JSON `{match, rules[]}` evaluated over contact fields + enrichment; source may be `odoo` for live pulls).
3. Compose queue generates per-recipient subject/body from the campaign brief (A/B split across `CampaignVariant` weights when enabled); recipients move pending→generated→approved.
4. Human approval gate unless org autopilot flag is cleared (`requireApproval` default true).
5. Send orchestrator per recipient checks suppression (hard gate), marketing-consent basis per channel (`safety/consent.ts channelRequiresConsent`), ChannelHealth paused/warmup daily caps, quiet hours — then dispatches through provider outbound and self-rate-limits by enqueueing the next recipient with `delayMs = 3600/ratePerHour` (`queue.ts:61-65` comment "One recipient per job").
6. Engagement: open pixel/click redirect via TrackedLink stamp `CampaignRecipient.openedAt/clickedAt/convertedAt`; inbound STOP keywords anywhere in the flow land in SuppressionEntry via the shared pipeline (`inbound-pipeline.ts:17-37`).
