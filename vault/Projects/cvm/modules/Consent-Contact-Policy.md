---
cortex-generated: true
title: consent-contact-policy
tags: [module]
---

# consent & contact policy

**Project:** [[cvm]] | **Confidence:** strongly_inferred | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/consent/`

purpose: append-only consent records, suppression entries, do-not-contact, quiet hours in customer timezone, frequency caps, contact policies per channel, policy packs.
path_prefixes: packages/modules/src/consent/
key_files: application/ (checkFrequency, checkQuietHours, checkSuppression, currentConsent, policyFor), http/routes.ts
entrypoints: consentRoutes
responsibilities: supply the ordered check functions the single PolicyGate runs; consent.* became evaluable AST fields in P5 exactly as ADR-012 promised.
invariants: consent withdrawal between approval and send suppresses the send (release-blocking test).
confidence: strongly_inferred

## Files (5+)

- `packages/modules/src/consent/application/consent.ts`
- `packages/modules/src/consent/application/contact.ts`
- `packages/modules/src/consent/domain/policy.ts`
- `packages/modules/src/consent/http/routes.ts`
- `packages/modules/src/consent/index.ts`

## API surface

- `PUT /contact-policies/:channel`
- `GET /contact-policies`
- `DELETE /suppressions/:id`
- `POST /suppressions`
- `GET /suppressions`
- `GET /customers/:id/contacts`
- `POST /customers/:id/consent`
- `GET /customers/:id/consent`
