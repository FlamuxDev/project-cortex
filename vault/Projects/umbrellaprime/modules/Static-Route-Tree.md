---
cortex-generated: true
title: static-route-tree
tags: [module]
---

# static route tree

**Project:** [[umbrellaprime]] | **Confidence:** inferred | **verified@** `b56420dad197`
**Owns:** `src/app/[locale]/,src/app/{robots,sitemap,manifest}.ts`

purpose: five pages × two locales plus SEO files.
path_prefixes: src/app/[locale]/, src/app/{robots,sitemap,manifest}.ts
key_files: src/app/[locale]/layout.tsx (locale validation via notFound, fonts Manrope + IBM Plex Sans Arabic both preload:false, Organization JSON-LD inline); page.tsx files for home/about/services/industries/contact/privacy; sitemap.ts with hreflang alternates
entrypoints: generateStaticParams emits exactly {ar,en}
responsibilities: services page anchors per service slug; metadata via src/lib/metadata.ts
invariants: unknown locale → notFound() before rendering
pitfalls: none observed
confidence: high

## Files (8+)

- `src/app/[locale]/about/page.tsx`
- `src/app/[locale]/contact/page.tsx`
- `src/app/[locale]/industries/page.tsx`
- `src/app/[locale]/layout.tsx`
- `src/app/[locale]/page.tsx`
- `src/app/[locale]/privacy/page.tsx`
- `src/app/[locale]/services/page.tsx`
- `src/app/sitemap.ts`
