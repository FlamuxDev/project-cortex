---
cortex-generated: true
title: mawid-ai flows
tags: [flows/project]
---

# Mawid-AI — Product Flows

End-to-end behaviors as verified from source. Files are the evidence trail.

## WhatsApp inbound → AI reply (the critical path)
**Trigger:** Meta POST /api/whatsapp/webhook (text or audio)
*[[mawid-ai]] · confidence: high*

trigger: Meta POST /api/whatsapp/webhook (text or audio)
steps: verify x-hub-signature-256 (WHATSAPP_APP_SECRET→FACEBOOK_APP_SECRET→META_APP_SECRET fallback) → resolve org (display number ↔ graph phone_number_id) → dedupe by whatsapp_message_id unique index (23505 tolerated) → upsert customer/conversation (open, ai_handled=true) → persist inbound + bump unread → FCM notify owner → if ai_handled: `generateAndSendAiReplyForInbound` (idempotency check on inbound wamid → 1.8s debounce → loadAgentContext → paymentsEnabled injection → credential resolve → token probe (forced if last_error) → typing indicator + renewal → createAgentTools(dryRun off) → runWhatsAppAgent → integrity guard → send → persist outbound + clear error + usage_stats)
files: apps/web/app/api/whatsapp/webhook/route.ts; packages/backend/src/whatsapp/{webhook,client,credentials,send-state}.ts; packages/ai/src/application/whatsapp-inbound/handle-inbound.ts; packages/ai/src/application/ai-agent/{agent,guard,context}.ts
confidence: high (read end-to-end)

**Files:**
- `apps/web/app/api/whatsapp/webhook/route.ts; packages/backend/src/whatsapp/{webhook`
- `client`
- `credentials`
- `send-state}.ts; packages/ai/src/application/whatsapp-inbound/handle-inbound.ts; packages/ai/src/application/ai-agent/{agent`
- `guard`
- `context}.ts`

## AI-driven booking
**Trigger:** customer asks to book inside WhatsApp thread
*[[mawid-ai]] · confidence: high*

trigger: customer asks to book inside WhatsApp thread
steps: agent calls search_availability → presents options → requires explicit customer yes naming service+time → book_appointment → domain `validateAndBookSlot` under `pg_advisory_xact_lock` → application `bookAppointment` sends confirmation message via messaging/lifecycle → guard grounds the reply in tool output
files: packages/ai/src/application/ai-agent/tools/{slot-query,appointments}.ts; packages/backend/src/domain/booking/book.ts; packages/backend/src/application/booking/book-appointment.ts
confidence: high

**Files:**
- `packages/ai/src/application/ai-agent/tools/{slot-query`
- `appointments}.ts; packages/backend/src/domain/booking/book.ts; packages/backend/src/application/booking/book-appointment.ts`

## Deposit payment
**Trigger:** booking rule requires deposit OR dashboard action
*[[mawid-ai]] · confidence: high*

trigger: booking rule requires deposit OR dashboard action
steps: validateAndBookSlot sets status pending_deposit (paymentsEnabled injected) → /api/dashboard/appointments/[id]/deposit-checkout creates Stripe session → customer pays → POST /api/stripe/webhook (signature verified) → checkout.session.completed flips status→scheduled
files: packages/backend/src/payments/stripe-appointment-deposit.ts; apps/web/app/api/stripe/webhook/route.ts:27-46
confidence: high

**Files:**
- `packages/backend/src/payments/stripe-appointment-deposit.ts; apps/web/app/api/stripe/webhook/route.ts:27-46`

## Reminder cron
**Trigger:** external cron hits GET /api/cron/appointment-reminders (Bearer/x-cron-secret/platform_settings.cron_secret; 503 unconfigured, 401 mismatch; Vercel x-vercel-cron honored)
*[[mawid-ai]] · confidence: high*

trigger: external cron hits GET /api/cron/appointment-reminders (Bearer/x-cron-secret/platform_settings.cron_secret; 503 unconfigured, 401 mismatch; Vercel x-vercel-cron honored)
steps: find upcoming appointments in offset windows → atomic JSONB claim on reminders_sent → render template bilingual → send per-org decrypted token → record ISO ts per offset
files: apps/web/app/api/cron/*/route.ts; apps/web/lib/cron/verify-cron-request.ts; packages/backend/src/application/messaging/reminders.ts
confidence: high

**Files:**
- `apps/web/app/api/cron/*/route.ts; apps/web/lib/cron/verify-cron-request.ts; packages/backend/src/application/messaging/reminders.ts`

## Auth (web + client apps)
**Trigger:** login/register or client-app bootstrap
*[[mawid-ai]] · confidence: high*

trigger: login/register or client-app bootstrap
steps: bcrypt password → users row; sessions carry token + refresh_token + expiry pair → web uses mawid_session cookie (middleware proxy.ts updateSession); desktop/mobile use Authorization Bearer + POST /api/auth/refresh rotation; password reset via hashed tokens + Resend email (allow-listed base URL)
files: apps/web/lib/auth/session.ts (:7 SESSION_COOKIE="mawid_session"; refreshSession :96), lib/auth/proxy.ts, lib/email/send.ts
confidence: high

**Files:**
- `apps/web/lib/auth/session.ts (:7 SESSION_COOKIE="mawid_session"; refreshSession :96)`
- `lib/auth/proxy.ts`
- `lib/email/send.ts`

## Deploy
**Trigger:** push to main
*[[mawid-ai]] · confidence: high*

trigger: push to main
steps: GH Actions builds standalone image (NEXT_PUBLIC_APP_URL=https://gomawid.com build-arg, gha cache) → pushes {latest,sha} → operator runs scripts/deploy-to-ec2.sh → rsync (secrets excluded) → server-up.sh: run migrations ORDER → ghcr login via ~/.ghcr-token PAT → compose pull app && up -d → curl /api/health
files: .github/workflows/deploy.yml; scripts/{deploy-to-ec2,server-up,run-migrations}.sh; docker-compose.prod.yml
confidence: high

**Files:**
- `.github/workflows/deploy.yml; scripts/{deploy-to-ec2`
- `server-up`
- `run-migrations}.sh; docker-compose.prod.yml`

## Desktop deep-link return
**Trigger:** OAuth/billing completes in system browser → mawid:// scheme
*[[mawid-ai]] · confidence: medium*

trigger: OAuth/billing completes in system browser → mawid:// scheme
steps: Tauri deep-link plugin → deep_link_to_web_url maps to web URLs (settings?tab=whatsapp, billing success/cancelled, deposit success/cancelled) → WebView navigates
files: apps/desktop/src-tauri/src/lib.rs; apps/desktop/README.md table
confidence: medium-high

**Files:**
- `apps/desktop/src-tauri/src/lib.rs; apps/desktop/README.md table`
