---
cortex-generated: true
title: client-api-layer-desktop-mobile-parity
tags: [module]
---

# Client API layer (desktop/mobile parity)

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `apps/web/lib/api-client/,mobile/,account/,email/,push/,uploads/,desktop/`

purpose: single typed client + bearer/refresh auth for desktop & Flutter clients.
path_prefixes: apps/web/lib/api-client/, mobile/, account/, email/, push/, uploads/, desktop/
key_files: api-client/{config,fetch,auth,endpoints/{dashboard,auth}} (+3 test files), mobile/stripe-return-urls.ts (allow-list), push/firebase.ts + send.ts (FCM fan-out on inbound messages), uploads/presign.ts (S3, 5MB default cap, purpose-scoped keys), email/send.ts (Resend; reset URL allow-listed against stripe-return host list), desktop/{desktop-chrome,native-bridge}.ts, desktop-releases.ts (/download page feed)
confidence: medium-high (breadth verified; deep behavior not traced line-by-line)

## Files (36+)

- `apps/desktop/scripts/tauri-prereq-checker.mjs`
- `apps/desktop/scripts/tauri-prereq-checker.test.mjs`
- `apps/web/app/api/account/delete/route.ts`
- `apps/web/app/api/mobile/bootstrap/route.ts`
- `apps/web/app/api/mobile/push-test/route.ts`
- `apps/web/app/api/mobile/push-token/route.ts`
- `apps/web/app/api/mobile/uploads/presign/route.ts`
- `apps/web/app/api/mobile/whatsapp/status/route.ts`
- `apps/web/app/dashboard/account/account-page-client.tsx`
- `apps/web/app/dashboard/account/page.tsx`
- `apps/web/components/desktop/desktop-chrome.tsx`
- `apps/web/components/desktop/desktop-title-bar.tsx`
- `apps/web/lib/account/delete-account.ts`
- `apps/web/lib/api-client/auth.test.ts`
- `apps/web/lib/api-client/auth.ts`
- `apps/web/lib/api-client/config.test.ts`
- `apps/web/lib/api-client/config.ts`
- `apps/web/lib/api-client/endpoints/auth.ts`
- `apps/web/lib/api-client/endpoints/dashboard.ts`
- `apps/web/lib/api-client/fetch.test.ts`
- `apps/web/lib/api-client/fetch.ts`
- `apps/web/lib/api-client/index.ts`
- `apps/web/lib/api-client/types.ts`
- `apps/web/lib/desktop/desktop-chrome.ts`
- `apps/web/lib/desktop/native-bridge.ts`

## API surface

- `GET Authorization`
- `PUT /api/mobile/push-token`
- `DELETE /api/mobile/push-token`
- `POST /api/mobile/uploads/presign`
- `GET /api/mobile/bootstrap`
- `POST /api/account/delete`
- `GET /api/mobile/whatsapp/status`
- `POST /api/mobile/push-test`
