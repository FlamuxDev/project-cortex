# CORTEX REPORT — FARAJ (farj-portfolio)

## META
project_id: faraj
root: /home/aboud/Dev/FARAJ/farj-portfolio
kind: bilingual (en/ar) personal portfolio site, statically prerendered Next.js app
languages: TypeScript (.ts), TSX (.tsx), CSS (single globals.css, ~1005 lines)
frameworks: Next.js 16.2.9 (App Router, Turbopack) · React 19.2.4 · Tailwind CSS v4 (@theme, no config file) · next/font
package_managers: npm (package-lock.json present)
test_frameworks: none found
deployment: no explicit target configured [inferred] — plain `next build`/`next start`, empty `next.config.ts`; NOT a git repository (no .git)

## OVERVIEW
Personal portfolio for Abdulrahman Faraj ("FARAJ"), a full-stack/AI engineer in Amman, Jordan positioning around Arabic-first AI products for MENA (src/lib/site.ts:8-53). The entire site is one long scrolling page rendered per locale under `/[locale]` — seven sections (hero, work, services, approach, stack, about, contact) composed in src/app/[locale]/page.tsx:34-46. There is no dynamic data anywhere: both locales are prerendered at build time via `generateStaticParams` (src/app/[locale]/layout.tsx:26-28).

Bilingualism is the core design constraint. All copy lives in `src/lib/content/` typed as `Localized<T> = Record<"en"|"ar", T>` (src/lib/i18n.ts:9), so a missing translation is a compile error, not a runtime gap. Arabic pages get full RTL treatment (`dir={dirForLocale(locale)}`, layout.tsx:51). `/` redirects to the visitor's best `Accept-Language` match via Next.js 16's `proxy.ts` convention (src/proxy.ts — replaces middleware).

Visual identity is deliberately dependency-free: "OpenClaw Dark" terminal-inspired theme with a single coral accent, defined entirely as CSS tokens in `@theme` blocks (src/styles/globals.css:17-63); motion is CSS + IntersectionObserver, zero animation libraries (README.md:12-14). The README calls the brand "Obsidian & Ember" but DESIGN.md and globals.css both say "OpenClaw Dark" — README appears stale.

## ARCHITECTURE
Three-layer static architecture:
1. **Content layer** — pure-TS bilingual data modules (`src/lib/content/*.ts`, 10 files) + identity single-source-of-truth `src/lib/site.ts` (domain, email, section ids drive nav/footer/sitemap/JSON-LD).
2. **Presentation layer** — server-rendered section components (`src/sections/*.tsx`) plus small UI/layout primitives (`src/components/{ui,layout,brand,work}`); client interactivity is limited to reveal-on-scroll, scroll-spy, marquee, rotating word.
3. **Route/metadata shell** — `[locale]` segment with metadata builders (`src/lib/seo.ts`), JSON-LD `@graph` injected in layout (layout.tsx:67-71), prerendered OG image, generated icons, sitemap with hreflang alternates (src/app/sitemap.ts), robots.
Locale negotiation sits in front: `src/proxy.ts` redirects bare paths; `matchLocale()` honors q-values (src/lib/i18n.ts:40-63).

## MODULES

### i18n-core — Locale system & redirect proxy
purpose: locale registry, direction mapping, Accept-Language matching, root redirect.
path_prefixes: src/lib/i18n.ts, src/proxy.ts
key_files: src/proxy.ts:10-23 (redirect logic), src/lib/i18n.ts:40-63 (`matchLocale` q-value ranking)
entrypoints: proxy runs on all non-asset routes (matcher excludes `_next`, `api`, dotted paths — proxy.ts:25-29)
responsibilities: every route locale-prefixed incl. default; unknown locales → notFound() in layout/page rather than broken dictionary (layout.tsx:44-46)
invariants: only two locales ("en","ar"); ar ⇒ rtl; matcher must never swallow static assets
pitfalls: `proxy` (not `middleware`) is a Next.js 16 convention — old knowledge breaks it
confidence: high

### content-layer — Bilingual copy & identity
purpose: all user-facing prose and identity data, type-enforced bilingual.
path_prefixes: src/lib/content/, src/lib/site.ts
key_files: src/lib/site.ts:8-41 (`site`, `sectionIds` — drives scroll-spy order), src/lib/content/types.ts (SectionCopy/Fact/Stat shapes), src/lib/content/index.ts
entrypoints: imported by sections, seo.ts, sitemap.ts
responsibilities: adding a string requires both languages or TS fails; adding a section = content module → section component → `sectionIds` entry → render in page.tsx (README.md:79-81)
invariants: `site.url` is the root of every canonical/hreflang URL (README.md:89-92)
pitfalls: editing copy means touching two language objects; forgetting `sectionIds` breaks scroll-spy
confidence: high

### page-shell — Routes, SEO, structured data
purpose: prerendered per-locale page + metadata machinery.
path_prefixes: src/app/
key_files: src/app/[locale]/layout.tsx (html lang/dir, fonts, noscript fallback for reveals, JSON-LD script), src/app/[locale]/opengraph-image.tsx, src/app/[locale]/not-found.tsx, src/app/robots.ts, src/app/sitemap.ts, src/app/icon.tsx, src/app/apple-icon.tsx, src/lib/seo.ts
entrypoints: Next App Router file conventions
responsibilities: per-locale metadata with canonical + hreflang + x-default; Person/Organization/WebSite/SoftwareApplication JSON-LD graph; serialized safely via `serializeJsonLd` (layout.tsx:69-70)
invariants: `<noscript>` style forces `.reveal` visible when JS disabled (layout.tsx:62-64) — accessibility floor
pitfalls: fonts split across two systems — Latin from Fontshare CDN @import in globals.css:1, Arabic via next/font (layout.tsx:16-21)
confidence: high

### sections-ui — Page sections & components
purpose: the seven page sections and their building-block components.
path_prefixes: src/sections/, src/components/
key_files: src/sections/{Hero,Work,Services,Approach,Stack,About,Contact}.tsx; src/components/ui/{Reveal,RotatingWord,Marquee,ScrollProgress...}; src/components/work/FeaturedWork.tsx; src/components/layout/Nav.tsx (scroll-spy), LocaleSwitch.tsx (`scroll={false}` to preserve position on switch — README.md:43-44)
entrypoints: composed only by src/app/[locale]/page.tsx
responsibilities: presentation only; narrative order "proof before pitch" documented inline (page.tsx:35-38)
invariants: motion = CSS + IntersectionObserver only, no JS animation libs
pitfalls: Reveal-style components start at opacity:0 — any new animated element must respect the noscript override
confidence: high

### design-tokens — Tailwind v4 CSS-first theming
purpose: single source of all colors/radii/type-scale/easings.
path_prefixes: src/styles/globals.css
key_files: globals.css:17-53 (`@theme` literal tokens: void/surface/ink/ember palette with contrast ratios annotated), globals.css:57-63 (`@theme inline` font stacks resolving next/font vars)
entrypoints: imported once in layout
responsibilities: no tailwind.config.ts exists; utilities like `bg-void`/`text-ember` stay in sync with hand-written CSS through shared custom properties (globals.css:12-16)
invariants: flat elevation — all shadow vars explicitly `none` (globals.css:65-72)
pitfalls: brand name drift — README says "Obsidian & Ember", DESIGN.md/globals.css say "OpenClaw Dark"
confidence: high

## FLOWS

### First visit / locale routing
trigger: GET on any path without a supported locale prefix.
steps: proxy.ts checks prefix → if absent, `matchLocale(Accept-Language)` picks en/ar honoring q-values → 302 to `/{locale}` (+ preserved path) → `[locale]/layout` validates locale (else notFound) → prerendered page streams.
files: src/proxy.ts, src/lib/i18n.ts, src/app/[locale]/layout.tsx
confidence: high

### Adding a content section
trigger: developer task.
steps: create `src/lib/content/<name>.ts` (Localized<T>) → add section component in src/sections/ → append id to `sectionIds` (site.ts:33-41) → import & render in page.tsx in desired order → nav/scroll-spy/sitemap follow automatically.
files: src/lib/content/, src/lib/site.ts, src/app/[locale]/page.tsx
confidence: high (documented README.md:79-81, matches code)

### In-page language switch
trigger: user clicks LocaleSwitch.
steps: navigate to opposite-locale path with `scroll={false}` → same scroll position kept on the mirrored RTL/LTR page.
files: src/components/layout/LocaleSwitch.tsx, src/lib/i18n.ts (`oppositeLocale`)
confidence: medium-high (README claim; component not read line-by-line)

## APIS
none — purely static pages. Route inventory:

| Route | Purpose | Evidence |
|---|---|---|
| `/` | redirect to locale | src/proxy.ts |
| `/[locale]` | the whole portfolio (7 sections) | src/app/[locale]/page.tsx |
| `/[locale]/opengraph-image` | prerendered OG card | src/app/[locale]/opengraph-image.tsx |
| `/sitemap.xml` | hreflang alternates | src/app/sitemap.ts |
| `/robots.txt` | robots | src/app/robots.ts |

## DATABASE
none/file-based — no storage of any kind; all data compiled into the bundle from src/lib/content/.

## TESTS
none found. package.json scripts are dev/build/start/lint only (package.json:5-10); no test dirs, no test deps. Only verification path is `npm run lint` (eslint-config-next) and manual review.

## GIT LESSONS
Not a git repository — `.git` absent, `git log` fails. No history, no blame, no rollback safety net. This is the single biggest process risk for this project (see RISKS). No shas available.

## DECISIONS
- Zero runtime/UI/state libraries: motion is CSS + IntersectionObserver (README.md:12-14; confirmed — deps are exactly next/react/react-dom).
- Type-enforced bilingualism: `Localized<T>` makes missing translations uncompilable (src/lib/i18n.ts:9, README.md:73-77).
- Tailwind v4 CSS-first: theme in `@theme` instead of config file (globals.css:17; README.md:83-85).
- Next.js 16 `proxy.ts` over middleware for locale redirect (src/proxy.ts:7-8).
- Accessibility floors built-in: skip-link, noscript un-hide of reveals, focus-visible styles, AA contrast ratios annotated in token comments (globals.css:25-36).
- Latin display/body fonts served from Fontshare CDN @import; only Arabic self-hosted via next/font (globals.css:1, layout.tsx:8-23).

## RISKS & TECH DEBT
- **No version control** — any edit is irreversible; first action should be `git init` + push to remote.
- README/brand-name mismatch ("Obsidian & Ember" vs "OpenClaw Dark") — docs drift already starting.
- Fontshare CDN @import in globals.css:1 is render-blocking and an external availability dependency for Latin text; Arabic (the primary audience) is fine via next/font.
- Year computed at build time (`new Date().getFullYear()`, page.tsx:20-21) — stale footer year if build not refreshed; deliberate but worth knowing.
- No tests, no CI; lint-only gate.
- `next.config.ts` is default-empty — no security headers, no image domains config; fine today since no dynamic content.

## UNCERTAIN
- Deployment target unknown [inferred]: nothing points to Vercel/static export/hosting config; `.next/` presence suggests local dev/build only.
- Why .git is missing [uncertain]: parent /home/aboud/Dev/FARAJ may have been intended as repo root or repo removed intentionally.
- `RotatingWord`, `StatusPill` internals not read individually; behavior inferred from names/README [inferred].
