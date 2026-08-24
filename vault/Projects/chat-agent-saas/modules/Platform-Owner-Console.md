---
cortex-generated: true
title: platform-owner-console
tags: [module]
---

# Platform owner console

**Project:** [[chat-agent-saas]] | **Confidence:** strongly_inferred | **verified@** `d5c6955acca7`
**Owns:** `packages/platform-admin/src/app/`

purpose: manage orgs, billing, system config, feature catalog, integration tokens; separate identity + noindex everywhere.
path_prefixes: packages/platform-admin/src/app/
key_files: src/app/(console)/, login/, providers.tsx
entrypoints: next start :5174 (PM2 chatagent-admin), nginx admin.botifyarabia.ai.conf.
responsibilities: super/operator roles via PLATFORM_ADMIN_JWT_SECRET; org suspension (Auth rejects ALL requests when Organization.status==='suspended'); Dynatrace platform-level token mgmt (migration 20260616190000).
invariants: entire tree robots noindex/nofollow/nocache; never shares tenant auth.
pitfalls: none recorded beyond generic.
confidence: strongly_inferred

## Files (18+)

- `packages/platform-admin/src/app/(console)/admins/page.tsx`
- `packages/platform-admin/src/app/(console)/ai-models/page.tsx`
- `packages/platform-admin/src/app/(console)/audit-log/page.tsx`
- `packages/platform-admin/src/app/(console)/billing/orgs/[orgId]/page.tsx`
- `packages/platform-admin/src/app/(console)/billing/page.tsx`
- `packages/platform-admin/src/app/(console)/demo-bookings/page.tsx`
- `packages/platform-admin/src/app/(console)/features/page.tsx`
- `packages/platform-admin/src/app/(console)/layout.tsx`
- `packages/platform-admin/src/app/(console)/mcp-servers/page.tsx`
- `packages/platform-admin/src/app/(console)/orgs/[orgId]/page.tsx`
- `packages/platform-admin/src/app/(console)/orgs/page.tsx`
- `packages/platform-admin/src/app/(console)/page.tsx`
- `packages/platform-admin/src/app/(console)/plans/page.tsx`
- `packages/platform-admin/src/app/(console)/pricing/page.tsx`
- `packages/platform-admin/src/app/(console)/system-config/page.tsx`
- `packages/platform-admin/src/app/layout.tsx`
- `packages/platform-admin/src/app/login/page.tsx`
- `packages/platform-admin/src/app/providers.tsx`
