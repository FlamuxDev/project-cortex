---
cortex-generated: true
title: next-js-operator-console
tags: [module]
---

# Next.js operator console

**Project:** [[cvm]] | **Confidence:** verified | **verified@** `2d7ffcee167d`
**Owns:** `apps/web/src/`

purpose: bilingual (en/ar RTL) permission-gated console; 100% RSC, zero client interface JS.
path_prefixes: apps/web/src/
key_files: src/proxy.ts, src/app/layout.tsx, src/app/(app)/layout.tsx, src/components/ui.tsx, src/components/band-rail.tsx, src/components/rule-builder.tsx, src/lib/api.ts (apiOrEmpty/mutate helpers), src/lib/api-types.ts (generated), src/lib/i18n.ts, src/lib/dictionaries/ar.ts, next.config.ts (static CSP)
entrypoints: `pnpm dev:web` (:3100); login page standalone.
responsibilities: 41 pages across 22 sections ((app)/customers|identity|audiences|offers|decisions|campaigns|deliveries|journeys|triggers|loyalty|games|models|analytics|data-quality|integrations|privacy|audit|administration|trace…); forms POST server actions answered 303 with ?error/?notice params; rule-builder round-trips AST as URL JSON; disclosure via `<details>`; no modals.
invariants: permissions gate navigation (absent, not disabled) while server re-checks; CSP `script-src 'self'` without unsafe-inline is LOAD-BEARING (keeps client router dead so native form posts carry Set-Cookie); apiOrEmpty distinguishes 403 from honest-empty; Arabic uses Latin digits (ar-u-nu-latn); dir set once on html; logical properties everywhere.
pitfalls: enabling per-request nonce broke sign-in + seven golden-path tests, reverted twice independently (0283a39, STATUS.md); renaming page headings broke 11 heading-based tests (reverted); `--text-muted`/`--border-strong` contrast failures found by redesign audit; Tailwind v4 needs `[var(--token)]` not v3 `[--token]` shorthand.
confidence: verified

## Files (40+)

- `apps/web/src/app/(app)/administration/page.tsx`
- `apps/web/src/app/(app)/administration/policy/page.tsx`
- `apps/web/src/app/(app)/administration/security/page.tsx`
- `apps/web/src/app/(app)/analytics/explore/page.tsx`
- `apps/web/src/app/(app)/analytics/page.tsx`
- `apps/web/src/app/(app)/audiences/[key]/page.tsx`
- `apps/web/src/app/(app)/audiences/page.tsx`
- `apps/web/src/app/(app)/audit/correlation/[id]/page.tsx`
- `apps/web/src/app/(app)/audit/page.tsx`
- `apps/web/src/app/(app)/campaigns/[code]/page.tsx`
- `apps/web/src/app/(app)/campaigns/[code]/runs/[id]/page.tsx`
- `apps/web/src/app/(app)/campaigns/page.tsx`
- `apps/web/src/app/(app)/customers/[id]/page.tsx`
- `apps/web/src/app/(app)/customers/page.tsx`
- `apps/web/src/app/(app)/data-quality/[sourceId]/page.tsx`
- `apps/web/src/app/(app)/data-quality/page.tsx`
- `apps/web/src/app/(app)/decisions/[id]/page.tsx`
- `apps/web/src/app/(app)/decisions/page.tsx`
- `apps/web/src/app/(app)/deliveries/[id]/page.tsx`
- `apps/web/src/app/(app)/games/[code]/page.tsx`
- `apps/web/src/app/(app)/games/page.tsx`
- `apps/web/src/app/(app)/identity/conflicts/[id]/page.tsx`
- `apps/web/src/app/(app)/identity/customers/[id]/page.tsx`
- `apps/web/src/app/(app)/identity/page.tsx`
- `apps/web/src/app/(app)/integrations/page.tsx`

## API surface

- `GET note`
- `GET threshold`
- `GET id`
- `GET reason`
- `GET expires_at`
- `GET channel`
- `GET identifier_type`
- `GET identifier_value`
- `GET customer_id`
- `GET enabled`
- `GET package`
- `GET default_role`
- `GET name`
- `GET max_concurrent_sessions`
- `GET require_mfa_for_all`
