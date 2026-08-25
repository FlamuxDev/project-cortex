---
cortex-generated: true
title: mawid-ai code map
tags: [codemap/project]
---

# Mawid-AI — Code Map

## Directory layout (indexed files)

- `apps/` — 293 files
- `packages/` — 71 files
- `scripts/` — 12 files
- `docker/` — 1 files
- `drizzle.config.ts/` — 1 files
- `eslint.config.mjs/` — 1 files

## Entry points

- `apps/web/app/api/dashboard/services/route.ts`
- `apps/web/app/api/whatsapp/webhook/route.ts`
- `apps/web/app/api/dashboard/resources/route.ts`
- `apps/web/app/api/dashboard/staff/route.ts`
- `apps/web/app/api/dashboard/appointments/route.ts`
- `apps/web/app/api/dashboard/templates/route.ts`
- `apps/web/app/api/dashboard/conversations/[id]/route.ts`
- `apps/web/app/api/dashboard/customers/[id]/details/route.ts`
- `apps/web/app/api/dashboard/org-hour-overrides/route.ts`
- `apps/web/app/api/dashboard/organization/route.ts`
- `apps/web/app/api/dashboard/scheduling/route.ts`
- `apps/web/app/api/instagram/webhook/route.ts`
- `apps/web/app/api/messenger/webhook/route.ts`
- `apps/web/app/api/mobile/push-token/route.ts`
- `apps/web/app/auth/callback/route.ts`

## Most-connected symbols (fan-in leaders)

| Symbol | Kind | Location |
|---|---|---|
| `cn` | function | `apps/web/lib/utils.ts:4` |
| `State` | interface | `apps/web/hooks/use-toast.ts:56` |
| `requireOrganizationApi` | function | `apps/web/lib/dashboard/org.ts:62` |
| `toast` | function | `apps/web/hooks/use-toast.ts:164` |
| `BookingRules` | interface | `packages/core/src/kernel/booking-rules.ts:16` |
| `Toast` | type | `apps/web/hooks/use-toast.ts:162` |
| `Ymd` | type | `packages/core/src/kernel/timezone.ts:45` |
| `mergeBookingRules` | function | `packages/core/src/kernel/booking-rules.ts:62` |
| `collectToolOutcomes` | function | `packages/ai/src/application/ai-agent/guard.ts:19` |
| `ToolOutcomes` | type | `packages/ai/src/application/ai-agent/guard.ts:11` |
| `wallClockToUtc` | function | `packages/core/src/kernel/timezone.ts:94` |
| `apiFetchJson` | function | `apps/web/lib/api-client/fetch.ts:126` |
| `resolveOrgTimezone` | function | `packages/core/src/kernel/timezone.ts:34` |
| `Appointment` | interface | `apps/web/components/dashboard/appointments-manager.tsx:43` |
| `Message` | interface | `apps/web/components/dashboard/conversation-view.tsx:23` |
| `getSessionUserFromRequest` | function | `apps/web/lib/auth/session.ts:44` |
| `intervalsOverlap` | function | `packages/backend/src/domain/booking/availability.ts:45` |
| `Appointment` | interface | `apps/web/components/dashboard/customers-table.tsx:43` |
| `Appointment` | interface | `apps/web/components/dashboard/upcoming-appointments.tsx:8` |
| `isPaymentsEnabled` | function | `packages/backend/src/infrastructure/platform/settings.ts:44` |
| `saveAuthTokens` | function | `apps/web/lib/api-client/auth.ts:72` |
| `rateLimit` | function | `apps/web/lib/rate-limit.ts:29` |
| `checkIntegrity` | function | `packages/ai/src/application/ai-agent/guard.ts:82` |
| `parseMetaMessagingWebhook` | function | `packages/backend/src/channels/meta-webhook.ts:60` |
| `formatInOrgTimezone` | function | `packages/core/src/kernel/timezone.ts:125` |
| `Label` | function | `apps/web/components/ui/label.tsx:8` |
| `verifyMetaWebhookSignature` | function | `packages/backend/src/whatsapp/webhook.ts:11` |
| `reset` | function | `apps/web/components/dashboard/ai-preview.tsx:63` |
| `reset` | function | `apps/web/components/landing/motion.tsx:269` |
| `reset` | function | `apps/web/components/landing/motion.tsx:158` |

## Highest-importance files

- `apps/web/app/api/dashboard/services/route.ts` (262 loc)
- `apps/web/app/api/whatsapp/webhook/route.ts` (341 loc)
- `apps/web/app/api/dashboard/resources/route.ts` (73 loc)
- `apps/web/app/api/dashboard/staff/route.ts` (149 loc)
- `apps/web/app/api/dashboard/appointments/route.ts` (516 loc)
- `apps/web/app/api/dashboard/templates/route.ts` (75 loc)
- `apps/web/components/dashboard/ops-hub.tsx` (251 loc)
- `apps/web/app/api/dashboard/conversations/[id]/route.ts` (78 loc)
- `apps/web/app/api/dashboard/customers/[id]/details/route.ts` (102 loc)
- `apps/web/app/api/dashboard/org-hour-overrides/route.ts` (68 loc)
- `apps/web/app/api/dashboard/organization/route.ts` (78 loc)
- `apps/web/app/api/dashboard/scheduling/route.ts` (34 loc)
- `apps/web/app/api/instagram/webhook/route.ts` (57 loc)
- `apps/web/app/api/messenger/webhook/route.ts` (55 loc)
- `apps/web/app/api/mobile/push-token/route.ts` (59 loc)
- `apps/web/app/auth/callback/route.ts` (9 loc)
- `apps/web/app/deposit/success/page.tsx` (84 loc)
- `apps/web/app/api/dashboard/setup-status/route.ts` (44 loc)
- `apps/web/lib/dashboard/ops-url.ts` (27 loc)
- `packages/backend/src/channels/webhook-verify.ts` (35 loc)
- `apps/web/app/dashboard/ops/ops-page-client.tsx` (165 loc)
- `apps/web/app/api/account/delete/route.ts` (34 loc)
- `apps/web/app/api/auth/change-password/route.ts` (45 loc)
- `apps/web/app/api/auth/forgot-password/route.ts` (49 loc)
- `apps/web/app/api/auth/login/route.ts` (47 loc)