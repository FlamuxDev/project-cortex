---
cortex-generated: true
title: tenant-web-app-next-js-16
tags: [module]
---

# Tenant web app (Next.js 16)

**Project:** [[chat-agent-saas]] | **Confidence:** verified | **verified@** `d5c6955acca7`
**Owns:** `packages/web/src/app/(app)/[locale]/,packages/web/src/app/(marketing)/[locale]/,packages/web/src/screens/`

purpose: auth screens + full dashboard (agents, conversations, analytics, knowledge, integrations UI, outreach, settings) + SEO marketing site.
path_prefixes: packages/web/src/app/(app)/[locale]/, packages/web/src/app/(marketing)/[locale]/, packages/web/src/screens/
key_files: src/i18n/routing.ts (localePrefix:'always', localeDetection OFF), two root layouts ((marketing) SSR vs (app) dark-only class="dark"), src/i18n/locales/{en,ar}.ts (~3.5k lines each react-i18next) vs messages/{en,ar}.json (next-intl), screens/*.tsx (~30 pages), utils/supportWorkspace.ts (hasPermission sidebar mirror)
entrypoints: next start :5173 (PM2 chatagent-web), nginx reverse proxy (infra/nginx/botifyarabia.ai.conf).
responsibilities: bilingual ar/en with RTL, Socket.IO client for live conversations, TanStack Query over axios, Recharts charts, embed preview, legacy-path 308 redirects.
invariants: dashboard strings go in react-i18next locales, marketing strings in next-intl messages — two stores BY DESIGN; (app) is dark-only (no theme toggle; client-side .dark broke first paint); `<html lang>` static in (app), swapped client-side; sidebar nav mirrors server permission gates but server remains the gate.
pitfalls: robots must never bounce Googlebot off `/` (localeDetection off, `/`→`/ar`); setting .dark from client effect regresses first paint.
confidence: verified

## Files (40+)

- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/actions/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/analytics/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/config/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/conversations/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/dynatrace/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/embed/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/integrations/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/issues/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/knowledge/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/mcp/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/odoo/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/outreach/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/playground/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/splunk/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/[agentId]/support/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/layout.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/settings/page.tsx`
- `packages/web/src/app/(app)/[locale]/dashboard/team/page.tsx`
- `packages/web/src/app/(app)/[locale]/demo/page.tsx`
- `packages/web/src/app/(app)/[locale]/forgot-password/page.tsx`
- `packages/web/src/app/(app)/[locale]/invite/page.tsx`
- `packages/web/src/app/(app)/[locale]/layout.tsx`
- `packages/web/src/app/(app)/[locale]/login/page.tsx`

## API surface

- `POST /auth/accept-invite`
- `GET token`
- `GET conversationId`
- `POST /outreach/email-domains`
- `GET /outreach/email-domains`
- `POST /dynatrace/connections`
- `GET /dynatrace/connections`
- `POST /auth/forgot-password`
- `GET /org/profile`
- `DELETE conversationId`
- `POST /outreach/journeys`
- `GET /outreach/segments`
- `GET /outreach/journeys`
- `POST /auth/login`
- `POST /mcp/servers`
