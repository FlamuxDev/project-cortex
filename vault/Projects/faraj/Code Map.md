---
cortex-generated: true
title: faraj code map
tags: [codemap/project]
---

# FARAJ — Code Map

## Directory layout (indexed files)

- `src/` — 44 files
- `eslint.config.mjs/` — 1 files
- `next-env.d.ts/` — 1 files
- `next.config.ts/` — 1 files
- `postcss.config.mjs/` — 1 files

## Entry points

- `src/lib/content/index.ts`
- `src/app/[locale]/layout.tsx`
- `src/app/[locale]/page.tsx`

## Most-connected symbols (fan-in leaders)

| Symbol | Kind | Location |
|---|---|---|
| `localePath` | function | `src/lib/i18n.ts:30` |
| `Locale` | type | `src/lib/i18n.ts:3` |
| `isLocale` | function | `src/lib/i18n.ts:17` |
| `dirForLocale` | function | `src/lib/i18n.ts:21` |
| `matchLocale` | function | `src/lib/i18n.ts:40` |
| `serializeJsonLd` | function | `src/lib/seo.ts:165` |
| `buildJsonLd` | function | `src/lib/seo.ts:103` |
| `buildMetadata` | function | `src/lib/seo.ts:46` |
| `LocaleLayout` | function | `src/app/[locale]/layout.tsx:41` |
| `generateMetadata` | function | `src/app/[locale]/layout.tsx:30` |
| `generateStaticParams` | function | `src/app/[locale]/layout.tsx:26` |
| `NotFound` | function | `src/app/[locale]/not-found.tsx:13` |
| `OpengraphImage` | function | `src/app/[locale]/opengraph-image.tsx:22` |
| `generateStaticParams` | function | `src/app/[locale]/opengraph-image.tsx:10` |
| `Home` | function | `src/app/[locale]/page.tsx:16` |
| `AppleIcon` | function | `src/app/apple-icon.tsx:10` |
| `Icon` | function | `src/app/icon.tsx:12` |
| `robots` | function | `src/app/robots.ts:4` |
| `sitemap` | function | `src/app/sitemap.ts:9` |
| `Logo` | function | `src/components/brand/Logo.tsx:14` |
| `Wordmark` | function | `src/components/brand/Wordmark.tsx:18` |
| `Atmosphere` | function | `src/components/layout/Atmosphere.tsx:9` |
| `Footer` | function | `src/components/layout/Footer.tsx:13` |
| `LocaleSwitch` | function | `src/components/layout/LocaleSwitch.tsx:42` |
| `Nav` | function | `src/components/layout/Nav.tsx:23` |
| `ScrollProgress` | function | `src/components/layout/ScrollProgress.tsx:12` |
| `Arrow` | function | `src/components/ui/Arrow.tsx:12` |
| `Chip` | function | `src/components/ui/Chip.tsx:13` |
| `Marquee` | function | `src/components/ui/Marquee.tsx:15` |
| `Reveal` | function | `src/components/ui/Reveal.tsx:38` |

## Highest-importance files

- `src/lib/i18n.ts` (64 loc)
- `src/lib/content/index.ts` (14 loc)
- `src/lib/site.ts` (54 loc)
- `src/lib/content/types.ts` (24 loc)
- `src/components/ui/Reveal.tsx` (85 loc)
- `src/components/ui/SectionHeader.tsx` (58 loc)
- `src/app/[locale]/layout.tsx` (76 loc)
- `src/app/[locale]/page.tsx` (52 loc)
- `src/components/ui/Arrow.tsx` (44 loc)
- `src/components/brand/Wordmark.tsx` (37 loc)
- `src/components/ui/Chip.tsx` (21 loc)
- `src/components/layout/Atmosphere.tsx` (18 loc)
- `src/components/ui/StatusPill.tsx` (17 loc)
- `src/lib/content/work.ts` (257 loc)
- `src/lib/seo.ts` (168 loc)
- `src/components/brand/Logo.tsx` (50 loc)
- `src/components/layout/Footer.tsx` (80 loc)
- `src/components/layout/LocaleSwitch.tsx` (87 loc)
- `src/components/layout/Nav.tsx` (173 loc)
- `src/components/layout/ScrollProgress.tsx` (49 loc)
- `src/components/ui/Marquee.tsx` (35 loc)
- `src/components/ui/RotatingWord.tsx` (52 loc)
- `src/components/work/FeaturedWork.tsx` (90 loc)
- `src/sections/About.tsx` (85 loc)
- `src/sections/Approach.tsx` (39 loc)