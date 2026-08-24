---
cortex-generated: true
title: next-js-web-application
tags: [module]
---

# Next.js Web Application

**Project:** [[mushagil]] | **Confidence:** verified | **verified@** `638838aad84d`
**Owns:** `apps/web`

purpose: bilingual (ar default) operator console consuming generated API client.
path_prefixes: apps/web
key_files: middleware.ts (locale redirect + dev-tenant cookie), app/[locale]/layout.tsx (root layout; no bare-root layout), lib/api-client.ts (createAuthenticatedApiClient), lib/server-tenant-context.ts, lib/error-messages.ts, lib/navigation.ts, lib/readiness-blockers.ts, components/AppShell/*
entrypoints: pages under app/[locale]: login, invitations/accept, workspaces, settings/{team,security,billing,platform-probes,business/*}, services, staff, onboarding
responsibilities: permission-safe navigation, all UI states incl. offline/error (NETWORK_UNAVAILABLE retryable pattern from M01 review), no optimistic success on committing actions.
invariants: Arabic RTL structural base; dev-tenant cookie never read in production (lib/server-tenant-context.ts refuses); RSC prefetch requests must not mint a second dev tenant id (middleware comment — real tenant-consistency bug they hit).
pitfalls: dev tenant cookie flow is M01 scaffolding predating real identity; two independent cookie mechanisms (dev-tenant vs session) coexist.
confidence: verified

