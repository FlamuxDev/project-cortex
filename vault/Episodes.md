---
cortex-generated: true
title: Episodes
tags: [episodes/cortex]
---

# Engineering Episodes

Validated knowledge extracted from completed tasks. Query via `cortex episode list` / packets' PAST TASK LESSONS.

## عدل نظام الحجوزات بحيث نتجنب duplicate creation
`mushagil` · partial · inferred
- **Lessons:** Idempotency checks for booking creation belong in business-capacity BookingPolicyService before any state transition.

## عدل نظام الحجوزات بحيث نتجنب duplicate creation
`mushagil` · partial · inferred
- **Problem:** duplicate booking creation when clients retry
- **Root cause:** booking policy service has no idempotency guard; retry path re-enters create
- **Lessons:** Booking dedupe must live in the business-capacity module: BookingPolicyService + policies.controller own draft/publish state machines, so any idempotency key check belongs there before state transition. Never retry create without a client request fingerprint.

## random task xyz
`mushagil` · abandoned · inferred
- **Problem:** random task xyz (deliberate error-path probe from /tmp)
- **Root cause:** Not a real task; cwd was /tmp outside any project.
- **Failed approaches:** Ran task start outside a project directory; cortex fell back to lexical detection and picked mushagil, fuzzy-matching 'random' to crypto.randomUUID() symbols — noise, not signal.

## وين الشي الي يمنع duplicate requests؟
`sham-v2` · partial · inferred
- **Problem:** وين الشي الي يمنع duplicate requests؟ (What prevents duplicate requests?)
- **Root cause:** Duplicate-request prevention exists but the packet missed it: idempotency_key TEXT NOT NULL UNIQUE in src/runtime/db.js schema; per-transition idempotencyKey replay check in src/runtime/workflow-engine.js (SELECT to_state FROM workflow_events WHERE instance_id=? AND idempotency_key=?); Meta webhook replays keyed by provider_message_id in src/channels/whatsapp/worker.js; outbox unique key in src/ru
- **Lessons:** sham-v2 duplicate-request prevention: every workflow transition carries an idempotencyKey checked against workflow_events(instance_id,idempotency_key) UNIQUE in runtime/workflow-engine.js before applying state, inbound WhatsApp events are keyed inbound:<provider_message_id> in channels/whatsapp/worker.js, and outbound sends rely on idempotency_key NOT NULL UNIQUE in runtime/db.js — search for 'ide

## وين نظام الحجوزات؟
`mawid-ai` · partial · inferred
- **Problem:** وين نظام الحجوزات؟ (Where is the booking system?)
- **Root cause:** نظام الحجوزات lives in packages/backend/src/domain/booking/ — book.ts (validateAndBookSlot :296, applyRescheduleWithSlotLock, acquireSlotBookingLock via pg_advisory_xact_lock), availability.ts, rules.ts; exposed via apps/web/app/api/dashboard/appointments/route.ts and the Gemini tool packages/ai/src/application/ai-agent/tools/appointments.ts.
- **Lessons:** Mawid-AI booking system: pure domain logic in packages/backend/src/domain/booking/{book,availability,rules}.ts with slot safety via pg_advisory_xact_lock in book.ts acquireSlotBookingLock; Arabic task terms map to English code terms (حجوزات → booking/appointments) — cortex packet handled this translation correctly

## Which tests should run if the campaign service changes?
`telvora` · partial · inferred
- **Problem:** Which tests should run if the campaign service changes?
- **Root cause:** Campaign service lives in services/core-api/internal/campaigns/ (handler.go Handler/requirePermission, execution.go, model.go, store.go); its direct unit suites are internal/campaigns/execution_test.go + ops_test.go plus e2e/tests/campaigns.spec.ts (Playwright B23 exit gate).
- **Lessons:** Telvora campaign service tests: change services/core-api/internal/campaigns/* → run go test ./internal/campaigns/ (execution_test.go threshold/approval paths, ops_test.go kill/pause) plus Playwright e2e/tests/campaigns.spec.ts; every Telvora Go module also carries an rls_test.go cross-tenant negative suite that should run when tenant scoping changes

## Change tenant authorization behavior
`luma` · partial · inferred
- **Problem:** Change tenant authorization behavior
- **Root cause:** Luma has no multi-tenant model — authorization is role-based JWT middleware: backend-luma/src/middlewares/authMiddlewares.js (authMiddleware, verifies JWT + role claim vs DB) and roleMiddleware.js/authorizeMiddleware.js (role gating per route). Packet correctly refused to suggest files (EVIDENCE WARNING on all 4 terms).
- **Lessons:** Luma authorization is single-tenant role-based: JWT verified in backend-luma/src/middlewares/authMiddlewares.js with a decoded-role-vs-DB-role consistency check (INVALID_ROLE_CLAIM), and per-route gating via roleMiddleware(...allowedRoles); there is no tenant_id anywhere — 'tenant' tasks should be reframed as role/RBAC tasks

## Where would I modify document ingestion?
`cvm` · partial · inferred
- **Problem:** Where would I modify document ingestion?
- **Root cause:** Document/data ingestion lives entirely in packages/modules/src/ingestion/ — REST intake in http/routes.ts (Ingestion API, /v1/ingest/*), validation pipeline in application/pipeline.ts (ingestChunk), contract registry in application/registry.ts, public facade index.ts. Modification point depends on layer: route validation vs chunk processing vs contract spec.
- **Lessons:** CVM document ingestion is a self-contained module under packages/modules/src/ingestion/: HTTP intake + sync validation in http/routes.ts, async processing via application/pipeline.ts ingestChunk, data contracts parsed by domain/contract.ts parseContractSpec; the module's only legal import path is its index.ts facade

## Fix duplicate booking creation on retry
`mushagil` · partial · inferred
- **Problem:** Fix duplicate booking creation on retry
- **Root cause:** Booking behavior lives in packages/modules/business-capacity/src/application/booking-policy-service.ts (BookingPolicyService, BookingPolicyView) plus domain/state-machines.ts; retry semantics live in the platform queue layer (QueueWrapper DLQ/retry tested by packages/database/tests/integration/queue-dlq-retry.test.ts). No literal 'duplicate' dedupe code found — matches packet EVIDENCE WARNING.
- **Lessons:** Mushagil booking policy logic is centralized in packages/modules/business-capacity/src/application/booking-policy-service.ts via BookingPolicyService with draft/publish state transitions in ../domain/state-machines.ts; queue retry/DLQ semantics are owned by @mushagil/platform QueueWrapper and integration-tested in packages/database/tests/integration/queue-dlq-retry.test.ts
