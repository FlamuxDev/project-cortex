---
cortex-generated: true
title: campify flows
tags: [flows/project]
---

# Campify — Product Flows

End-to-end behaviors as verified from source. Files are the evidence trail.

## signup-verify-workspace-invite (CUJ-1)
**Trigger:** POST /v1/auth/signup (or web form → /api/signup proxy)
*[[campify]] · confidence: verified*

trigger: POST /v1/auth/signup (or web form → /api/signup proxy)
steps: 1. throttle(5/min, ip-keyed) + zod 2. signUp creates user + verification token (scrypt pw) 3. if EmailPort+PUBLIC_WEB_URL configured: send verification email, else echo token only when exposeVerificationToken=true (non-prod/tests) 4. verifyEmail consumes token 5. login sets httpOnly SameSite=Lax cookie (host-only) 6. createWorkspace assigns owner membership + default plan 7. inviteMember (owner/admin only, throttled) emails bound link → /invitation page accepts with session, binding to invitee address.
files: apps/api/src/app.ts, packages/core/src/identity/service.ts, apps/web/src/app/api/login/route.ts, apps/web/src/lib/actions.ts
confidence: verified

**Files:**
- `apps/api/src/app.ts`
- `packages/core/src/identity/service.ts`
- `apps/web/src/app/api/login/route.ts`
- `apps/web/src/lib/actions.ts`

## csv-import (CUJ-2)
**Trigger:** upload in /app/contacts/import
*[[campify]] · confidence: verified*

trigger: upload in /app/contacts/import
steps: 1. base64 file → createImportPreview parses CSV/XLSX (bounded), normalizes, dedupes, persists plan rows 2. UI shows summary + sample + mapping 3. optional remap re-previews 4. commitImport applies plan creating/updating contacts + audit.
files: packages/core/src/imports/{sheet,dryRun,commit}.ts, apps/api/src/app.ts:1082
confidence: verified

**Files:**
- `packages/core/src/imports/{sheet`
- `dryRun`
- `commit}.ts`
- `apps/api/src/app.ts:1082`

## consent-to-send (CUJ-3)
**Trigger:** POST …/consent or suppression, then any send attempt
*[[campify]] · confidence: verified*

trigger: POST …/consent or suppression, then any send attempt
steps: 1. recordConsent supersedes previous current row (trigger) 2. at execution dispatch calls checkSendAllowed → evaluateSendGate (suppression FIRST, then exact-channel granted required) 3. blocked ⇒ delivery_attempt 'suppressed' + message failed permanently.
files: packages/core/src/consent/{gate,repository}.ts, packages/core/src/delivery/dispatch.ts:136
confidence: verified

**Files:**
- `packages/core/src/consent/{gate`
- `repository}.ts`
- `packages/core/src/delivery/dispatch.ts:136`

## segment-build-and-snapshot (CUJ-4)
**Trigger:** /app/segments builder
*[[campify]] · confidence: verified*

trigger: /app/segments builder
steps: 1. AST validated client-side shape → POST segments/preview returns count+sample (compiled parameterised SQL) 2. save dynamic segment 3. campaign audience selects segments 4. approval freezes static snapshot member ids under repeatable read.
files: packages/core/src/segments/{ast,compile}.ts, packages/core/src/campaigns/approval.ts
confidence: verified

**Files:**
- `packages/core/src/segments/{ast`
- `compile}.ts`
- `packages/core/src/campaigns/approval.ts`

## campaign-launch (CUJ-5)
**Trigger:** builder tabs → submit
*[[campify]] · confidence: verified*

trigger: builder tabs → submit
steps: 1. configure basics/audience/channels/content/tracking 2. blockers computed (missing consent surface, unfrozen content…) 3. submit→in_review 4. approve by non-submitter with segments:write-class rights: audience certified, active version frozen, status scheduled 5. worker tickCampaignStarts flips scheduled→running (engine actor) + materializeMessages inserts one row per recipient×variant 6. worker claims batches (skip locked) → dispatch gates → port.send → status/attempts updated 7. pause/stop per state machine; emergency-stop endpoint halts mid-flight.
files: packages/core/src/campaigns/{state,approval,blockers}.ts, apps/worker/src/main.ts:52, packages/core/src/delivery/dispatch.ts, apps/api/src/deliveryRoutes.ts
confidence: verified

**Files:**
- `packages/core/src/campaigns/{state`
- `approval`
- `blockers}.ts`
- `apps/worker/src/main.ts:52`
- `packages/core/src/delivery/dispatch.ts`
- `apps/api/src/deliveryRoutes.ts`

## journey-execution (CUJ-6)
**Trigger:** publish journey
*[[campify]] · confidence: verified*

trigger: publish journey
steps: 1. canvas edits draft graph (immutable published version on publish) 2. worker polls entry criteria → enrollDueContacts creates enrollments 3. steps claimed → executeStep advances (wait schedules future, branch evaluates, task creates sales_task, send inserts message row) 4. message flows through the SAME campaign dispatch path.
files: packages/core/src/journeys/{enroll,execute,wait}.ts, apps/worker/src/main.ts:98
confidence: verified

**Files:**
- `packages/core/src/journeys/{enroll`
- `execute`
- `wait}.ts`
- `apps/worker/src/main.ts:98`

## engagement-attribution (CUJ-7)
**Trigger:** provider webhook or partner POST …/events
*[[campify]] · confidence: verified*

trigger: provider webhook or partner POST …/events
steps: 1. Resend Svix-HMAC verify over raw bytes, replay-bounded, idempotent on svix-id → applyProviderDeliveryEvent updates message status; bounce/complaint auto-suppresses 2. partner events ingested via API key 3. conversions attributed last-touch within windowDays of contact's most recent send 4. report/dashboard reconcile; CSV export available; ROI withheld when incomplete.
files: apps/api/src/providerWebhookRoutes.ts, packages/core/src/delivery/providerEventIngest.ts, packages/core/src/analytics/{repository,attribution,roi}.ts
confidence: verified

**Files:**
- `apps/api/src/providerWebhookRoutes.ts`
- `packages/core/src/delivery/providerEventIngest.ts`
- `packages/core/src/analytics/{repository`
- `attribution`
- `roi}.ts`

## outbound-webhook-delivery
**Trigger:** any of 8 domain events with active subscription
*[[campify]] · confidence: verified*

trigger: any of 8 domain events with active subscription
steps: 1. emission inserts webhook_deliveries 2. worker claims → signs payload (HMAC, timestamped) 3. WebhookHttpPort posts (urlGuard SSRF checks) 4. non-2xx/timeout retries backoff up to MAX_ATTEMPTS 5. redeliver endpoint forces requeue.
files: packages/core/src/webhooks/{dispatch,signing,urlGuard}.ts, packages/adapters/webhook-http/src/index.ts
confidence: verified

**Files:**
- `packages/core/src/webhooks/{dispatch`
- `signing`
- `urlGuard}.ts`
- `packages/adapters/webhook-http/src/index.ts`
