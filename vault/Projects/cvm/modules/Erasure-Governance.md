---
cortex-generated: true
title: erasure-governance
tags: [module]
---

# erasure & governance

**Project:** [[cvm]] | **Confidence:** strongly_inferred | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/privacy/`

purpose: right-to-erasure requests (approval-gated, irreversible): personal data removed, audit trail intact, aggregates unmoved — payload KEY REMOVAL only through the one narrow append-only breach path; processing register; jurisdiction consent packs; hashed compliance exports.
path_prefixes: packages/modules/src/privacy/
key_files: privacy/application/, http/routes.ts
entrypoints: privacyRoutes (/v1/erasure-requests*, /erasure-scope, /governance/*)
invariants: erasure cannot rewrite WHAT happened, only WHO it was about (ADR README Phase 7).
pitfalls: quarantined-row erasure is substring-matched — malformed identifier text evades it (known limitation 10).
confidence: strongly_inferred

## Files (4+)

- `packages/modules/src/privacy/application/erasure.ts`
- `packages/modules/src/privacy/application/governance.ts`
- `packages/modules/src/privacy/http/routes.ts`
- `packages/modules/src/privacy/index.ts`

## API surface

- `POST /governance/exports`
- `GET /governance/exports`
- `POST /governance/consent-packs/:code/activate`
- `PUT /governance/consent-packs/:code`
- `GET /governance/consent-packs`
- `GET /governance/processing-register`
- `POST /erasure-requests/:id/decision`
- `POST /customers/:id/erasure`
- `GET /erasure-scope`
- `GET /erasure-requests`
