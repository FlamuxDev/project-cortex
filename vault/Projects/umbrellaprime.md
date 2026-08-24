---
cortex-generated: true
title: umbrellaprime
tags: [project]
---

# umbrellaprime

**Path:** `/home/aboud/Dev/umbrellaprime`  
**Kind:** app | **Languages:** .tsx,.ts,.mjs,.js | **Frameworks:** None

**HEAD:** `b56420dad197` | **Brain:** `b56420dad197` | FRESH

| Files | Symbols | Modules | Flows | APIs | DB | Tests | Decisions | Memories |
|---|---|---|---|---|---|---|---|---|
| 59 | 89 | 6 | 4 | 0 | 0 | 4 | 8 | 14 (0 stale) |

## Modules
- [[umbrellaprime/modules/Client-Form-Validation-Sharing|client form + validation sharing]] — accessible bilingual form posting directly to Lambda. [inferred]
- [[umbrellaprime/modules/Cloudfront-Function-Local-Twin|CloudFront function & local twin]] — make clean URLs work on exact-key S3; reproduce identically in tests. [inferred]
- [[umbrellaprime/modules/Email-Handler|email handler]] — validate + throttle + email submissions via Resend. [inferred]
- [[umbrellaprime/modules/Locales-Dictionaries|locales & dictionaries]] — typed ar/en dictionaries, direction, trailing-slash-aware hrefs. [inferred]
- [[umbrellaprime/modules/Static-Route-Tree|static route tree]] — five pages × two locales plus SEO files. [inferred]
- [[umbrellaprime/modules/Tokens-Primitives|tokens & primitives]] — navy/gold dark identity, layout primitives, accessibility basics. [inferred]

## Flows
- **First visit routing** — GET / (or deep link).
- **Contact submission end-to-end** — user submits /{locale}/contact/ form.
- **E2E with production fidelity** — `npm run test:e2e`.
- **Deploy** — operator follows DEPLOY.md or scripts/deploy.sh.

## Key knowledge
- Architecture [strongly_inferred]
- Database [strongly_inferred]
- API surface [strongly_inferred]
- Historical lessons [verified]
- umbrellaprime: overview [verified]
- Tests & commands [verified]
