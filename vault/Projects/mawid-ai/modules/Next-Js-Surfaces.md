---
cortex-generated: true
title: next-js-surfaces
tags: [module]
---

# Next.js surfaces

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `apps/web/app/`

purpose: marketing site, auth pages, owner dashboard, admin, all API routes.
path_prefixes: apps/web/app/
key_files: app/api/** (59 route.ts), dashboard/{overview,business,calendar,settings,setup,account,billing,ops}, admin/{leads,organizations}, public/openapi.json + api-docs.html (/api-docs redirect, next.config.mjs redirects block)
invariants: setup wizard fully optional/non-gated (no SetupGuard — deleted); dashboard auth via `requireOrganizationApi` (apps/web/lib/dashboard/org.ts:62); i18n via dictionaries, no [locale] URL segments
confidence: high

## Files (40+)

- `apps/web/app/admin/layout.tsx`
- `apps/web/app/admin/leads/page.tsx`
- `apps/web/app/admin/loading.tsx`
- `apps/web/app/admin/organizations/page.tsx`
- `apps/web/app/admin/page.tsx`
- `apps/web/app/api/account/delete/route.ts`
- `apps/web/app/api/auth/change-password/route.ts`
- `apps/web/app/api/auth/forgot-password/route.ts`
- `apps/web/app/api/auth/login/route.ts`
- `apps/web/app/api/auth/logout/route.ts`
- `apps/web/app/api/auth/me/route.ts`
- `apps/web/app/api/auth/refresh/route.ts`
- `apps/web/app/api/auth/register/route.ts`
- `apps/web/app/api/auth/reset-password/route.ts`
- `apps/web/app/api/booking/available-slots/route.ts`
- `apps/web/app/api/conversations/[id]/messages/route.ts`
- `apps/web/app/api/cron/appointment-no-show/route.ts`
- `apps/web/app/api/cron/appointment-reminders/route.ts`
- `apps/web/app/api/cron/recurring-appointments/route.ts`
- `apps/web/app/api/dashboard/ai/preview/route.ts`
- `apps/web/app/api/dashboard/appointments/[id]/cancel/route.ts`
- `apps/web/app/api/dashboard/appointments/[id]/deposit-checkout/route.ts`
- `apps/web/app/api/dashboard/appointments/route.ts`
- `apps/web/app/api/dashboard/billing/checkout/route.ts`
- `apps/web/app/api/dashboard/billing/portal/route.ts`

## API surface

- `GET id`
- `GET host`
- `GET hub.challenge`
- `GET hub.verify_token`
- `GET hub.mode`
- `GET next`
- `GET c`
- `GET ai`
- `GET unread`
- `GET cancelled`
- `GET kind`
- `GET /api/cron/recurring-appointments`
- `POST /api/leads`
- `POST /api/auth/reset-password`
- `GET /api/dashboard/billing`
