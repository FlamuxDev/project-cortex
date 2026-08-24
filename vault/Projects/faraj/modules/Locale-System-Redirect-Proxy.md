---
cortex-generated: true
title: locale-system-redirect-proxy
tags: [module]
---

# Locale system & redirect proxy

**Project:** [[faraj]] | **Confidence:** inferred | **verified@** ``
**Owns:** `src/lib/i18n.ts,src/proxy.ts`

purpose: locale registry, direction mapping, Accept-Language matching, root redirect.
path_prefixes: src/lib/i18n.ts, src/proxy.ts
key_files: src/proxy.ts:10-23 (redirect logic), src/lib/i18n.ts:40-63 (`matchLocale` q-value ranking)
entrypoints: proxy runs on all non-asset routes (matcher excludes `_next`, `api`, dotted paths — proxy.ts:25-29)
responsibilities: every route locale-prefixed incl. default; unknown locales → notFound() in layout/page rather than broken dictionary (layout.tsx:44-46)
invariants: only two locales ("en","ar"); ar ⇒ rtl; matcher must never swallow static assets
pitfalls: `proxy` (not `middleware`) is a Next.js 16 convention — old knowledge breaks it
confidence: high

## Files (2+)

- `src/lib/i18n.ts`
- `src/proxy.ts`
