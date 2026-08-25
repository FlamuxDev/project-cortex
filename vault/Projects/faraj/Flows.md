---
cortex-generated: true
title: faraj flows
tags: [flows/project]
---

# FARAJ — Product Flows

End-to-end behaviors as verified from source. Files are the evidence trail.

## First visit / locale routing
**Trigger:** GET on any path without a supported locale prefix.
*[[faraj]] · confidence: high*

trigger: GET on any path without a supported locale prefix.
steps: proxy.ts checks prefix → if absent, `matchLocale(Accept-Language)` picks en/ar honoring q-values → 302 to `/{locale}` (+ preserved path) → `[locale]/layout` validates locale (else notFound) → prerendered page streams.
files: src/proxy.ts, src/lib/i18n.ts, src/app/[locale]/layout.tsx
confidence: high

**Files:**
- `src/proxy.ts`
- `src/lib/i18n.ts`
- `src/app/[locale]/layout.tsx`

## Adding a content section
**Trigger:** developer task.
*[[faraj]] · confidence: high*

trigger: developer task.
steps: create `src/lib/content/<name>.ts` (Localized<T>) → add section component in src/sections/ → append id to `sectionIds` (site.ts:33-41) → import & render in page.tsx in desired order → nav/scroll-spy/sitemap follow automatically.
files: src/lib/content/, src/lib/site.ts, src/app/[locale]/page.tsx
confidence: high (documented README.md:79-81, matches code)

**Files:**
- `src/lib/content/`
- `src/lib/site.ts`
- `src/app/[locale]/page.tsx`

## In-page language switch
**Trigger:** user clicks LocaleSwitch.
*[[faraj]] · confidence: medium*

trigger: user clicks LocaleSwitch.
steps: navigate to opposite-locale path with `scroll={false}` → same scroll position kept on the mirrored RTL/LTR page.
files: src/components/layout/LocaleSwitch.tsx, src/lib/i18n.ts (`oppositeLocale`)
confidence: medium-high (README claim; component not read line-by-line)

**Files:**
- `src/components/layout/LocaleSwitch.tsx`
- `src/lib/i18n.ts (`oppositeLocale`)`
