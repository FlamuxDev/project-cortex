---
cortex-generated: true
title: offer-catalog
tags: [module]
---

# offer catalog

**Project:** [[cvm]] | **Confidence:** strongly_inferred | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/catalog/`

purpose: offers with sixteen §11 fields, immutable versions, separation-of-duties approval, transactional capacity (offer_inventory CHECK constraint prevents oversell).
path_prefixes: packages/modules/src/catalog/
key_files: application/ (incl. offerabilityProblems consumed by gate), http/routes.ts
entrypoints: catalogRoutes (/v1/offers*)
responsibilities: expose offerability checks to PolicyGate; inventory reservation via conditional UPDATE WHERE (no SELECT FOR UPDATE serialisation).
invariants: unapproved offer never returned by a decision (gate 1 evidence).
confidence: strongly_inferred

## Files (7+)

- `packages/modules/src/catalog/application/eligibility.ts`
- `packages/modules/src/catalog/application/inventory.ts`
- `packages/modules/src/catalog/application/offers.ts`
- `packages/modules/src/catalog/domain/offer.ts`
- `packages/modules/src/catalog/http/routes.ts`
- `packages/modules/src/catalog/index.ts`
- `packages/modules/src/catalog/jobs.ts`

## API surface

- `POST /offers/:code/eligibility-preview`
- `PUT /offers/:code/inventory`
- `POST /offers/:code/archive`
- `POST /offers/:code/versions/:version/publish`
- `POST /offers/:code/versions/:version/approval`
- `POST /offers/:code/versions/:version/request-approval`
- `POST /offers/:code/versions`
- `GET /offers/:code`
- `POST /offers`
- `GET /offers`
- `POST /products`
- `GET /products`
