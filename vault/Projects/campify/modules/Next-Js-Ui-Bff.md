---
cortex-generated: true
title: next-js-ui-bff
tags: [module]
---

# Next.js UI + BFF

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `apps/web/src`

purpose: public site, private app UI, server actions, i18n ar/en RTL.
path_prefixes: apps/web/src
key_files: apps/web/src/middleware.ts, lib/actions.ts, lib/api.ts, lib/i18n.ts, app/(public)/*, app/(app)/*
entrypoints: middleware (session gate + noindex); /api/login,/api/signup proxies; server actions for all mutations
responsibilities: session validated (not shape-checked) per navigation, failing closed; actions carry intent only — rules live in core/API; campaign builder tabs, segment builder, journey canvas, import wizard, team screen.
invariants: /app never indexable (edge header + middleware + robots + automated test, ADR-0009); tokens consumed then redirected away (Next serializes searchParams into RSC payload/history/Referer).
pitfalls: `?next` validated by origin comparison, never regex; waitForURL-before-click race pattern broke tests 3× (PROGRESS.md M15/M18).
confidence: verified

## Files (40+)

- `apps/web/src/app/(app)/app/analytics/page.tsx`
- `apps/web/src/app/(app)/app/campaigns/[id]/audience/page.tsx`
- `apps/web/src/app/(app)/app/campaigns/[id]/channels/page.tsx`
- `apps/web/src/app/(app)/app/campaigns/[id]/content/page.tsx`
- `apps/web/src/app/(app)/app/campaigns/[id]/page.tsx`
- `apps/web/src/app/(app)/app/campaigns/[id]/report/page.tsx`
- `apps/web/src/app/(app)/app/campaigns/[id]/review/page.tsx`
- `apps/web/src/app/(app)/app/campaigns/page.tsx`
- `apps/web/src/app/(app)/app/contacts/[id]/page.tsx`
- `apps/web/src/app/(app)/app/contacts/import/[jobId]/page.tsx`
- `apps/web/src/app/(app)/app/contacts/import/page.tsx`
- `apps/web/src/app/(app)/app/contacts/page.tsx`
- `apps/web/src/app/(app)/app/crm/deals/[id]/page.tsx`
- `apps/web/src/app/(app)/app/crm/page.tsx`
- `apps/web/src/app/(app)/app/journeys/[id]/page.tsx`
- `apps/web/src/app/(app)/app/journeys/page.tsx`
- `apps/web/src/app/(app)/app/page.tsx`
- `apps/web/src/app/(app)/app/plan/page.tsx`
- `apps/web/src/app/(app)/app/sales-tasks/[id]/page.tsx`
- `apps/web/src/app/(app)/app/sales-tasks/page.tsx`
- `apps/web/src/app/(app)/app/segments/page.tsx`
- `apps/web/src/app/(app)/app/team/page.tsx`
- `apps/web/src/app/(app)/app/templates/page.tsx`
- `apps/web/src/app/(app)/layout.tsx`
- `apps/web/src/app/(public)/invitation/page.tsx`

## API surface

- `GET ai_suggestions`
- `GET sends`
- `GET /v1/me`
- `GET x-forwarded-proto`
- `GET host`
- `POST /v1/invitations/accept`
- `GET password`
- `GET email`
- `GET displayName`
- `GET file`
- `POST /v1/auth/logout`
- `POST /v1/workspaces`
- `POST /api/login`
- `POST /api/signup`
- `GET /api/campaigns/[id]/report.csv`
