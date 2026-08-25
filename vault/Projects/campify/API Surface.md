---
cortex-generated: true
title: campify api
tags: [api/project]
---

# Campify — API Surface

67 routes. Grouped by owning file; every route names its handler.

## `apps/api/src/app.ts`

- **GET** `/healthz` → `async`
- **GET** `/readyz` → `async`
- **POST** `/v1/auth/login` → `async`
- **POST** `/v1/auth/logout` → `async`
- **POST** `/v1/auth/signup` → `async`
- **POST** `/v1/auth/verify` → `async`
- **POST** `/v1/invitations/accept` → `async`
- **GET** `/v1/me` → `async`
- **POST** `/v1/workspaces` → `async`
- **GET** `/v1/workspaces/:workspaceId/audit` → `async`
- **POST** `/v1/workspaces/:workspaceId/contact-fields` → `async`
- **GET** `/v1/workspaces/:workspaceId/contact-fields` → `async`
- **POST** `/v1/workspaces/:workspaceId/contacts` → `async`
- **GET** `/v1/workspaces/:workspaceId/contacts` → `async`
- **DELETE** `/v1/workspaces/:workspaceId/contacts/:id` → `async`
- **GET** `/v1/workspaces/:workspaceId/contacts/:id` → `async`
- **POST** `/v1/workspaces/:workspaceId/contacts/:id/consent` → `async`
- **GET** `/v1/workspaces/:workspaceId/contacts/:id/tags` → `async`
- **DELETE** `/v1/workspaces/:workspaceId/contacts/:id/tags/:tagId` → `async`
- **PUT** `/v1/workspaces/:workspaceId/contacts/:id/tags/:tagId` → `async`
- **GET** `/v1/workspaces/:workspaceId/imports/:jobId` → `async`
- **POST** `/v1/workspaces/:workspaceId/imports/:jobId/commit` → `async`
- **PUT** `/v1/workspaces/:workspaceId/imports/:jobId/mapping` → `async`
- **POST** `/v1/workspaces/:workspaceId/imports/preview` → `async`
- **GET** `/v1/workspaces/:workspaceId/invitations` → `async`
- **POST** `/v1/workspaces/:workspaceId/invitations` → `async`
- **DELETE** `/v1/workspaces/:workspaceId/invitations/:id` → `async`
- **POST** `/v1/workspaces/:workspaceId/lists` → `async`
- **GET** `/v1/workspaces/:workspaceId/lists` → `async`
- **DELETE** `/v1/workspaces/:workspaceId/lists/:listId/contacts/:id` → `async`
- **PUT** `/v1/workspaces/:workspaceId/lists/:listId/contacts/:id` → `async`
- **PATCH** `/v1/workspaces/:workspaceId/members/:userId` → `async`
- **DELETE** `/v1/workspaces/:workspaceId/members/:userId` → `async`
- **POST** `/v1/workspaces/:workspaceId/segments` → `async`
- **GET** `/v1/workspaces/:workspaceId/segments` → `async`
- **POST** `/v1/workspaces/:workspaceId/segments/:id/recount` → `async`
- **POST** `/v1/workspaces/:workspaceId/segments/:id/snapshot` → `async`
- **POST** `/v1/workspaces/:workspaceId/segments/preview` → `async`
- **POST** `/v1/workspaces/:workspaceId/suppressions` → `async`
- **POST** `/v1/workspaces/:workspaceId/tags` → `async`
- …and 1 more

## `apps/api/src/campaignRoutes.ts`

- **GET** `/v1/workspaces/:workspaceId/members` → `async`
- **POST** `/v1/workspaces/:workspaceId/templates` → `async`
- **GET** `/v1/workspaces/:workspaceId/templates` → `async`

## `apps/api/src/deliveryRoutes.ts`

- **POST** `/v1/workspaces/:workspaceId/campaigns/:id/quiet-hours-override` → `async`
- **POST** `/v1/workspaces/:workspaceId/campaigns/:id/test-recipients` → `async`
- **POST** `/v1/workspaces/:workspaceId/campaigns/:id/test-send` → `async`

## `apps/api/src/providerWebhookRoutes.ts`

- **POST** `/v1/providers/resend/webhook` → `async`

## `apps/web/src/app/(app)/app/plan/page.tsx`
*module: [[campify/modules/Next-Js-Ui-Bff|next-js-ui-bff]]*

- **GET** `ai_suggestions` [client]
- **GET** `sends` [client]

## `apps/web/src/app/(app)/app/team/page.tsx`
*module: [[campify/modules/Next-Js-Ui-Bff|next-js-ui-bff]]*

- **GET** `/v1/me` [client]
- **GET** `host` [client]
- **GET** `x-forwarded-proto` [client]

## `apps/web/src/app/(public)/invitation/page.tsx`
*module: [[campify/modules/Next-Js-Ui-Bff|next-js-ui-bff]]*

- **POST** `/v1/invitations/accept` → { token } [client]

## `apps/web/src/app/api/campaigns/[id]/report.csv/route.ts`
*module: [[campify/modules/Next-Js-Ui-Bff|next-js-ui-bff]]*

- **GET** `/api/campaigns/[id]/report.csv` → exported GET

## `apps/web/src/app/api/login/route.ts`
*module: [[campify/modules/Next-Js-Ui-Bff|next-js-ui-bff]]*

- **POST** `/api/login` → exported POST
- **GET** `email`
- **GET** `password`

## `apps/web/src/app/api/signup/route.ts`
*module: [[campify/modules/Next-Js-Ui-Bff|next-js-ui-bff]]*

- **POST** `/api/signup` → exported POST
- **GET** `displayName`
- **GET** `email`
- **GET** `password`

## `apps/web/src/lib/actions.ts`
*module: [[campify/modules/Next-Js-Ui-Bff|next-js-ui-bff]]*

- **POST** `/v1/auth/logout` → {}
- **POST** `/v1/workspaces` → { name, locale }
- **GET** `file`

## `apps/web/src/lib/api.ts`
*module: [[campify/modules/Next-Js-Ui-Bff|next-js-ui-bff]]*

- **GET** `/v1/me`

## `packages/core/src/imports/sheet.ts`
*module: [[campify/modules/Csv-Xlsx-Dry-Run-Then-Commit|csv-xlsx-dry-run-then-commit]]*

- **GET** `xl/sharedStrings.xml`
