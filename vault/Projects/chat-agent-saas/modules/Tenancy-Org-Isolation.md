---
cortex-generated: true
title: tenancy-org-isolation
tags: [module]
---

# tenancy / org isolation

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Tenant root = `Organization` (uuid, slug unique, status, soft-delete `deletedAt`, per-org AI defaults + BYOK keys encrypted, `schema.prisma:12-64`). Every domain table carries `orgId` (or reaches it via agent). There is **no Postgres RLS** — isolation is entirely query-layer discipline, guarded by an e2e suite (`__e2e__/tenant-isolation.e2e.test.ts`).
- Org-level feature flags live in `Organization.settings` JSONB and gate routes via `requireOrgFeature` (`middleware/orgFeature.ts:6-24`; resolution order documented at `schema.prisma:1776-1778`: org override → PlanFeature.enabled → catalog default).
- Suspension kill-switch enforced at login, refresh, authenticate, webhook gate, and chat (`assertOrgActive`, `chat.service.ts:861`).

