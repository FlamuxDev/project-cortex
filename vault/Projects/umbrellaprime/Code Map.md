---
cortex-generated: true
title: umbrellaprime code map
tags: [codemap/project]
---

# umbrellaprime — Code Map

## Directory layout (indexed files)

- `src/` — 43 files
- `tests/` — 4 files
- `infra/` — 3 files
- `lambda/` — 2 files
- `eslint.config.mjs/` — 1 files
- `next-env.d.ts/` — 1 files
- `next.config.ts/` — 1 files
- `playwright.config.ts/` — 1 files
- `postcss.config.mjs/` — 1 files
- `scripts/` — 1 files
- `vitest.config.ts/` — 1 files

## Entry points

- `src/app/[locale]/about/page.tsx`
- `src/app/[locale]/contact/page.tsx`
- `src/app/[locale]/industries/page.tsx`
- `src/app/[locale]/layout.tsx`
- `src/app/[locale]/page.tsx`
- `src/app/[locale]/privacy/page.tsx`
- `src/app/[locale]/services/page.tsx`
- `src/app/layout.tsx`
- `src/app/page.tsx`

## Most-connected symbols (fan-in leaders)

| Symbol | Kind | Location |
|---|---|---|
| `localeHref` | function | `src/lib/i18n.ts:29` |
| `isLocale` | function | `src/lib/i18n.ts:11` |
| `Locale` | type | `src/lib/i18n.ts:6` |
| `getDictionary` | function | `src/lib/i18n.ts:15` |
| `Dictionary` | type | `src/content/en.ts:523` |
| `cloudfrontFunctionUri` | function | `infra/cloudfront-function.mjs:5` |
| `buildMetadata` | function | `src/lib/metadata.ts:4` |
| `handler` | function | `lambda/contact/index.mjs:60` |
| `handler` | function | `infra/cloudfront-function.js:9` |
| `buildContactSchema` | function | `src/lib/validation.ts:4` |
| `direction` | function | `src/lib/i18n.ts:19` |
| `AboutPage` | function | `src/app/[locale]/about/page.tsx:25` |
| `generateMetadata` | function | `src/app/[locale]/about/page.tsx:9` |
| `ContactPage` | function | `src/app/[locale]/contact/page.tsx:26` |
| `generateMetadata` | function | `src/app/[locale]/contact/page.tsx:10` |
| `IndustriesPage` | function | `src/app/[locale]/industries/page.tsx:25` |
| `generateMetadata` | function | `src/app/[locale]/industries/page.tsx:9` |
| `LocaleLayout` | function | `src/app/[locale]/layout.tsx:43` |
| `generateMetadata` | function | `src/app/[locale]/layout.tsx:33` |
| `generateStaticParams` | function | `src/app/[locale]/layout.tsx:29` |
| `HomePage` | function | `src/app/[locale]/page.tsx:23` |
| `generateMetadata` | function | `src/app/[locale]/page.tsx:13` |
| `PrivacyPage` | function | `src/app/[locale]/privacy/page.tsx:25` |
| `generateMetadata` | function | `src/app/[locale]/privacy/page.tsx:9` |
| `ServicesPage` | function | `src/app/[locale]/services/page.tsx:25` |
| `generateMetadata` | function | `src/app/[locale]/services/page.tsx:9` |
| `RootLayout` | function | `src/app/layout.tsx:12` |
| `manifest` | function | `src/app/manifest.ts:7` |
| `RootRedirect` | function | `src/app/page.tsx:20` |
| `robots` | function | `src/app/robots.ts:7` |

## Highest-importance files

- `src/content/en.ts` (525 loc)
- `src/lib/i18n.ts` (41 loc)
- `src/components/ui/Container.tsx` (26 loc)
- `src/lib/constants.ts` (22 loc)
- `src/components/ui/SectionHeading.tsx` (41 loc)
- `src/lib/metadata.ts` (44 loc)
- `src/app/[locale]/about/page.tsx` (87 loc)
- `src/app/[locale]/contact/page.tsx` (116 loc)
- `src/app/[locale]/industries/page.tsx` (73 loc)
- `src/app/[locale]/layout.tsx` (73 loc)
- `src/app/[locale]/page.tsx` (45 loc)
- `src/app/[locale]/privacy/page.tsx` (67 loc)
- `src/app/[locale]/services/page.tsx` (89 loc)
- `src/app/layout.tsx` (15 loc)
- `src/app/page.tsx` (49 loc)
- `src/components/layout/nav-items.ts` (11 loc)
- `src/components/layout/LanguageSwitcher.tsx` (37 loc)
- `src/components/ui/Button.tsx` (47 loc)
- `infra/cloudfront-function.mjs` (10 loc)
- `src/lib/validation.ts` (32 loc)
- `src/components/brand/ArcMotif.tsx` (31 loc)
- `src/components/brand/Logo.tsx` (52 loc)
- `src/components/brand/ServiceIcons.tsx` (129 loc)
- `src/components/sections/CompanyFacts.tsx` (28 loc)
- `lambda/contact/index.mjs` (106 loc)