# CORTEX REPORT — umbrellaprime

## META
project_id: umbrellaprime
root: /home/aboud/Dev/umbrellaprime
kind: bilingual (ar/en, Arabic-default) corporate marketing site — Next.js static export to S3+CloudFront, contact form via Lambda Function URL
languages: TypeScript (.ts/.tsx), JavaScript (Lambda .mjs, CloudFront Function)
frameworks: Next.js 16.2.12 (`output: "export"`) · React 19.2.4 · Tailwind CSS v4 (@theme) · Zod v4 · Resend (email)
package_managers: npm (package-lock.json; overrides for sharp/postcss)
test_frameworks: Vitest 3 (unit) · Playwright (e2e against real export) · Node built-in test runner (lambda + infra)
deployment: AWS S3 (private bucket + Origin Access Control) + CloudFront + ACM, region me-south-1; Lambda Function URL for contact; full runbook in DEPLOY.md; scripts/deploy.sh + package-lambda.sh

## OVERVIEW
Marketing site for Umbrella Prime Company, a Saudi LLC in Riyadh selling enterprise technology consulting, software engineering, infrastructure, and managed IT services (README.md:1-5). Five routes per locale (/about/, /services/, /industries/, /contact/, /privacy/ under /ar/ and /en/), all statically exported to out/ with trailing slashes because the production host is a private S3 bucket that only resolves exact object keys.

The defining architectural constraint is **static export has no server**: no middleware/proxy and no Server Actions exist in production. Consequences are handled explicitly: the root `/` is a hand-rolled redirect shell using navigator.language + meta-refresh fallback defaulting to Arabic (src/app/page.tsx), clean URLs are rewritten at the CloudFront edge (infra/cloudfront-function.js) with an identical rewrite implemented locally in scripts/static-server.mjs so e2e tests exercise real production behavior, and the contact form POSTs straight from the browser to a Lambda Function URL instead of a Server Action (README.md:42-56).

Content is bilingual typed dictionaries (src/content/{ar,en}.ts) with no i18n library; Arabic is the default locale. The form uses the same Zod schema builder client-side and a looser English-only backstop inside the Lambda (defense in depth — any client can be bypassed). Per the brief, the site references only verified company facts — no client names, certifications, or metrics anywhere.

## ARCHITECTURE
Four deployable pieces:
1. **Static site** — src/app with `[locale]` segment, `generateStaticParams` over ["ar","en"], `trailingSlash: true`, unoptimized images (next.config.ts:3-7); sections composed under src/components/sections/.
2. **Contact Lambda** — lambda/contact/index.mjs on a Function URL: method check → per-IP rate limit → JSON parse → loose Zod schema → Resend send; honest `{status:"not-configured"}` when env vars absent.
3. **Edge function** — infra/cloudfront-function.js viewer-request rewriting `/ar/about/` → `/ar/about/index.html` (private S3+OAC gives no directory-index resolution).
4. **Local prod-fidelity server** — scripts/static-server.mjs applies the same rewrite so Playwright tests the real thing (playwright.config.ts webServer builds the actual export).

Cross-cutting libs: src/lib/{i18n,metadata,structured-data,validation,constants}.ts shared by app and (validation concepts) Lambda; brand tokens as CSS-first @theme in src/app/globals.css (navy/gold extracted from logo artwork, single dark surface, RTL font swap via :root[dir=rtl]).

## MODULES

### i18n-content — locales & dictionaries
purpose: typed ar/en dictionaries, direction, trailing-slash-aware hrefs.
path_prefixes: src/lib/i18n.ts, src/content/
key_files: src/lib/i18n.ts:29-38 (`localeHref` keeps trailing slash + preserves #hash), src/content/ar.ts & en.ts (Dictionary type exported from en.ts, ar must satisfy it structurally)
entrypoints: every layout/page imports getDictionary(locale)
responsibilities: defaultLocale = "ar"; alternateLocale map for switcher/hreflang
invariants: all internal links go through localeHref (slash contract required by S3 key layout)
pitfalls: Dictionary type lives in en.ts — adding a field to en but not ar fails only where ar is consumed as Dictionary [inferred]
confidence: high

### pages-routes — static route tree
purpose: five pages × two locales plus SEO files.
path_prefixes: src/app/[locale]/, src/app/{robots,sitemap,manifest}.ts
key_files: src/app/[locale]/layout.tsx (locale validation via notFound, fonts Manrope + IBM Plex Sans Arabic both preload:false, Organization JSON-LD inline); page.tsx files for home/about/services/industries/contact/privacy; sitemap.ts with hreflang alternates
entrypoints: generateStaticParams emits exactly {ar,en}
responsibilities: services page anchors per service slug; metadata via src/lib/metadata.ts
invariants: unknown locale → notFound() before rendering
pitfalls: none observed
confidence: high

### contact-form — client form + validation sharing
purpose: accessible bilingual form posting directly to Lambda.
path_prefixes: src/components/forms/ContactForm.tsx, src/lib/validation.ts
key_files: ContactForm.tsx:36-83 (SubmitState machine incl. honest not-configured state; honeypot field pretends success without sending; success ONLY when Lambda answers {status:"sent"}), validation.ts:4-19 (buildContactSchema takes localized error MESSAGES so one schema serves both languages; consent literal("true"); phone digit-count refine; honeypot max(0))
entrypoints: rendered by /[locale]/contact/page.tsx
responsibilities: native HTML validation layered under Zod; NEXT_PUBLIC_CONTACT_API_URL read at build time (static export)
invariants: never fake success; honeypot hidden via clip technique chosen after off-canvas offset caused horizontal overflow (comment at line 87)
pitfalls: env var is baked at build — changing Lambda URL requires rebuild
confidence: high

### contact-lambda — email handler
purpose: validate + throttle + email submissions via Resend.
path_prefixes: lambda/contact/index.mjs (+ index.test.mjs, function.zip committed)
key_files: index.mjs:8-22 (per-container in-memory rate limit 5/10min — explicitly marked ponytail ceiling with DynamoDB upgrade path), index.mjs:27-34 (loose English schema; full localized validation already ran client-side), index.mjs:57-59 (CORS belongs to Function URL config, NOT response headers — duplicates break browsers), index.mjs:86-88 (not-configured is 200 with status)
entrypoints: Function URL (POST only)
responsibilities: reply-to set to submitter; base64 body handling
invariants: no secrets in code; RESEND_API_KEY etc. set on the function itself
pitfalls: rate limit warms per container only — not a global guarantee
confidence: high

### edge-static-serving — CloudFront function & local twin
purpose: make clean URLs work on exact-key S3; reproduce identically in tests.
path_prefixes: infra/, scripts/static-server.mjs
key_files: infra/cloudfront-function.js:9-20 (append index.html for dir URIs and dot-less paths), cloudfront-function.test.mjs (node --test coverage of rewrite logic)
entrypoints: attached viewer-request on distribution; scripts invoked by npm start / playwright webServer
responsibilities: parity between prod and test URL resolution
invariants: trailingSlash:true in next.config.ts is what makes the file layout match this scheme
confidence: high

### design-system — tokens & primitives
purpose: navy/gold dark identity, layout primitives, accessibility basics.
path_prefixes: src/components/{ui,brand,layout}/, src/app/globals.css
key_files: globals.css:7-39 (@theme palette + fade-in keyframes), globals.css:51-53 (RTL font swap), globals.css:60-70 (.ltr-embed bidi isolation for numerals/emails in Arabic copy; WCAG focus-visible ring), SkipLink.tsx, LanguageSwitcher.tsx, MobileNavigation.tsx, WhatsAppButton.tsx
entrypoints: imported via root/locale layouts
responsibilities: SectionHeading/Button/Container primitives; ArcMotif/ServiceIcons brand SVGs
invariants: single deliberate dark surface — no light/dark toggle (globals.css:3-6)
confidence: high

## FLOWS

### First visit routing
trigger: GET / (or deep link).
steps: `/` shell runs inline script reading navigator.language → location.replace("/ar/" or "/en/") → noscript meta-refresh fallback defaults to /ar/ → manual anchor links as last resort (src/app/page.tsx:11-44). Deep links hit CloudFront Function rewrite → exact S3 object.
files: src/app/page.tsx, infra/cloudfront-function.js
confidence: high

### Contact submission end-to-end
trigger: user submits /{locale}/contact/ form.
steps: FormData → buildContactSchema(localizedMessages).safeParse → invalid: flatten first error per field, role="alert" render → honeypot filled? fake success, stop → no CONTACT_API_URL? honest not-configured state → POST JSON to Lambda Function URL → Lambda re-validates loose schema, rate-limits by IP, sends via Resend → UI flips to success only on {status:"sent"}; not-configured/error surfaces honestly.
files: src/components/forms/ContactForm.tsx:36-83, src/lib/validation.ts, lambda/contact/index.mjs:60-105
confidence: high

### E2E with production fidelity
trigger: `npm run test:e2e`.
steps: playwright webServer command force-clears NEXT_PUBLIC_CONTACT_API_URL (shell beats .env.production.local in precedence) → builds real static export → serves via scripts/static-server.mjs with S3-exact-key behavior → 15 specs across navigation/mobile-menu/contact-form (incl. the unset-env "not configured" path).
files: playwright.config.ts:17-27, tests/e2e/*.spec.ts
confidence: high

### Deploy
trigger: operator follows DEPLOY.md or scripts/deploy.sh.
steps: build → sync out/ to private bucket (OAC) → CloudFront distribution + ACM cert (us-east-1) + Function attach → DNS at external registrar → package/upload Lambda (scripts/package-lambda.sh) → set function env vars.
files: DEPLOY.md (exact AWS CLI commands), scripts/deploy.sh
confidence: medium-high (runbook read partially)

## APIS

| Method | Path | Purpose | Evidence |
|---|---|---|---|
| POST | Lambda Function URL (NEXT_PUBLIC_CONTACT_API_URL) | contact-form email; statuses sent/not-configured/error; CORS on resource config | lambda/contact/index.mjs |
| GET/HEAD | /{locale}/{page}/ | static objects via CloudFront→S3(OAC) | next.config.ts, infra/cloudfront-function.js |

Site routes: /ar/ & /en/ (+ about/services/industries/contact/privacy each), robots.txt, sitemap.xml, manifest.webmanifest — README.md:24-40.

## DATABASE
none/file-based — no database anywhere. State: out/ static artifacts; lambda/contact/function.zip; two stray Arabic-named .xlsx files (violations lists) sitting untracked at repo root, unrelated to the app runtime.

## TESTS
Four-layer suite, all wired into `npm run test:all`:
- Unit: Vitest — tests/unit/validation.test.ts (schema logic), `npm test`. README records 7/7 passing pre-handoff.
- Infra: `npm run test:infra` — node --test infra/cloudfront-function.test.mjs (rewrite logic), 3/3.
- Lambda: `npm run test:lambda` (cd lambda/contact && npm test), handler logic 5/5.
- E2E: Playwright chromium — tests/e2e/{navigation,mobile-menu,contact-form}.spec.ts, 15/15, run against the genuine export with prod URL resolution (playwright.config.ts).
Also `npm run lint`, `npm run typecheck` gates documented as clean in README.md:122-133.

## GIT LESSONS
Only 4 commits (ff05525 first commit → b56420d):
- d844b04 "Convert to static export for S3/CloudFront hosting" — the pivotal architecture change; everything about routing/testing strategy flows from this decision.
- b56420d isolated Playwright builds by pinning NEXT_PUBLIC_CONTACT_API_URL empty in the e2e webServer — lesson: build-time-inlined public env vars leak between test and prod contexts unless forced.
- Lesson-by-absence: features went in almost whole in the first commit; history offers little archaeology. Working tree has two untracked .xlsx data files that should be gitignored or moved.
No branches beyond main evident from log sample.

## DECISIONS
- Static export + S3/CloudFront/OAC over a Node server (or Vercel): cheapest Saudi-friendly hosting; accepted cost is losing proxy/Server Actions (README.md:13, DEPLOY.md architecture diagram).
- Edge-rewrites instead of S3 website endpoint: keeps bucket private (AWS-recommended OAC pattern), at the price of needing the rewrite replicated locally for tests.
- Client-side root redirect with triple fallback (script/meta-refresh/manual links) since no server-side Accept-Language negotiation exists.
- One Zod schema builder parameterized by localized messages; Lambda keeps a deliberately looser English-only schema as pure security backstop.
- Honest-state UX: form refuses to claim success unless Lambda confirms; missing config renders as explicit state, not silent failure (README.md:77-79).
- Honeypot over captcha; clip-based hiding after off-canvas caused overflow (ContactForm.tsx:87-91).
- brand-source/ kept on disk but gitignored — originals preserved, derivatives committed (README.md:58-66).
- sharp/postcss version overrides + allowScripts pinning in package.json.

## RISKS & TECH DEBT
- Lambda rate limiting is per-container only (explicit ponytail comment) — no global abuse ceiling until DynamoDB/API-GW plan swap.
- NEXT_PUBLIC_CONTACT_API_URL baked at build time; rotating the Lambda URL means redeploying the whole site.
- Launch blockers tracked in README.md:142-151: privacy-policy legal review, Resend sending-domain verification, DNS access outside AWS.
- Two untracked Arabic .xlsx files at repo root (unrelated violation-list spreadsheets) — clutter/gitignore hygiene.
- No CI config found; test:all exists but nothing enforces it.
- Root redirect shell ships `robots: noindex` (good) but is a flashable intermediate page for JS browsers.
- function.zip committed in-repo — binary artifact drift risk vs package-lambda.sh output.

## UNCERTAIN
- scripts/static-server.mjs and scripts/deploy.sh internals not read line-by-line [inferred from README/playwright config].
- Whether deployment in DEPLOY.md has actually been executed (DNS/ACM steps pending per README "still needs your input") [uncertain].
- Exact parity guarantees of static-server.mjs with CloudFront Function edge cases (encoded URIs etc.) untested beyond the 3 infra unit cases [uncertain].
