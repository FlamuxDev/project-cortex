---
cortex-generated: true
title: routes-seo-structured-data
tags: [module]
---

# Routes, SEO, structured data

**Project:** [[faraj]] | **Confidence:** inferred | **verified@** ``
**Owns:** `src/app/`

purpose: prerendered per-locale page + metadata machinery.
path_prefixes: src/app/
key_files: src/app/[locale]/layout.tsx (html lang/dir, fonts, noscript fallback for reveals, JSON-LD script), src/app/[locale]/opengraph-image.tsx, src/app/[locale]/not-found.tsx, src/app/robots.ts, src/app/sitemap.ts, src/app/icon.tsx, src/app/apple-icon.tsx, src/lib/seo.ts
entrypoints: Next App Router file conventions
responsibilities: per-locale metadata with canonical + hreflang + x-default; Person/Organization/WebSite/SoftwareApplication JSON-LD graph; serialized safely via `serializeJsonLd` (layout.tsx:69-70)
invariants: `<noscript>` style forces `.reveal` visible when JS disabled (layout.tsx:62-64) — accessibility floor
pitfalls: fonts split across two systems — Latin from Fontshare CDN @import in globals.css:1, Arabic via next/font (layout.tsx:16-21)
confidence: high

## Files (8+)

- `src/app/[locale]/layout.tsx`
- `src/app/[locale]/not-found.tsx`
- `src/app/[locale]/opengraph-image.tsx`
- `src/app/[locale]/page.tsx`
- `src/app/apple-icon.tsx`
- `src/app/icon.tsx`
- `src/app/robots.ts`
- `src/app/sitemap.ts`
