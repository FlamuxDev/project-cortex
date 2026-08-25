---
cortex-generated: true
title: umbrellaprime flows
tags: [flows/project]
---

# umbrellaprime — Product Flows

End-to-end behaviors as verified from source. Files are the evidence trail.

## First visit routing
**Trigger:** GET / (or deep link).
*[[umbrellaprime]] · confidence: high*

trigger: GET / (or deep link).
steps: `/` shell runs inline script reading navigator.language → location.replace("/ar/" or "/en/") → noscript meta-refresh fallback defaults to /ar/ → manual anchor links as last resort (src/app/page.tsx:11-44). Deep links hit CloudFront Function rewrite → exact S3 object.
files: src/app/page.tsx, infra/cloudfront-function.js
confidence: high

**Files:**
- `src/app/page.tsx`
- `infra/cloudfront-function.js`

## Contact submission end-to-end
**Trigger:** user submits /{locale}/contact/ form.
*[[umbrellaprime]] · confidence: high*

trigger: user submits /{locale}/contact/ form.
steps: FormData → buildContactSchema(localizedMessages).safeParse → invalid: flatten first error per field, role="alert" render → honeypot filled? fake success, stop → no CONTACT_API_URL? honest not-configured state → POST JSON to Lambda Function URL → Lambda re-validates loose schema, rate-limits by IP, sends via Resend → UI flips to success only on {status:"sent"}; not-configured/error surfaces honestly.
files: src/components/forms/ContactForm.tsx:36-83, src/lib/validation.ts, lambda/contact/index.mjs:60-105
confidence: high

**Files:**
- `src/components/forms/ContactForm.tsx:36-83`
- `src/lib/validation.ts`
- `lambda/contact/index.mjs:60-105`

## E2E with production fidelity
**Trigger:** `npm run test:e2e`.
*[[umbrellaprime]] · confidence: high*

trigger: `npm run test:e2e`.
steps: playwright webServer command force-clears NEXT_PUBLIC_CONTACT_API_URL (shell beats .env.production.local in precedence) → builds real static export → serves via scripts/static-server.mjs with S3-exact-key behavior → 15 specs across navigation/mobile-menu/contact-form (incl. the unset-env "not configured" path).
files: playwright.config.ts:17-27, tests/e2e/*.spec.ts
confidence: high

**Files:**
- `playwright.config.ts:17-27`
- `tests/e2e/*.spec.ts`

## Deploy
**Trigger:** operator follows DEPLOY.md or scripts/deploy.sh.
*[[umbrellaprime]] · confidence: medium*

trigger: operator follows DEPLOY.md or scripts/deploy.sh.
steps: build → sync out/ to private bucket (OAC) → CloudFront distribution + ACM cert (us-east-1) + Function attach → DNS at external registrar → package/upload Lambda (scripts/package-lambda.sh) → set function env vars.
files: DEPLOY.md (exact AWS CLI commands), scripts/deploy.sh
confidence: medium-high (runbook read partially)

**Files:**
- `DEPLOY.md (exact AWS CLI commands)`
- `scripts/deploy.sh`
