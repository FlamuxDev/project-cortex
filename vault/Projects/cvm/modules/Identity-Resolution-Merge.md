---
cortex-generated: true
title: identity-resolution-merge
tags: [module]
---

# identity resolution & merge

**Project:** [[cvm]] | **Confidence:** verified | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/identity/`

purpose: deterministic cross-source resolution into canonical customers; ambiguous cases raise identity_conflict (never auto-merge); reversible merge/unmerge; probabilistic review queue (P10); rules configuration.
path_prefixes: packages/modules/src/identity/
key_files: application/resolve.ts, merge.ts, conflicts.ts, rules.ts, probabilistic-review.ts; jobs.ts
entrypoints: identityRoutes (/v1/identity/*)
responsibilities: publish `identity.changed` outbox events in the same txn as change (ADR-006) naming surviving/merged/restored customer ids.
invariants: merge→unmerge restores profile/timeline/features exactly (golden-path v3 assertion).
pitfalls: reading only one payload key left the other party describing "a person who no longer exists in that shape" (worker main.ts comment).
confidence: verified

## Files (12+)

- `packages/modules/src/identity/application/conflicts.ts`
- `packages/modules/src/identity/application/customers.ts`
- `packages/modules/src/identity/application/merge.ts`
- `packages/modules/src/identity/application/probabilistic-review.ts`
- `packages/modules/src/identity/application/resolve.ts`
- `packages/modules/src/identity/application/rules.ts`
- `packages/modules/src/identity/domain/identifiers.ts`
- `packages/modules/src/identity/domain/probabilistic.ts`
- `packages/modules/src/identity/domain/resolution.ts`
- `packages/modules/src/identity/http/routes.ts`
- `packages/modules/src/identity/index.ts`
- `packages/modules/src/identity/jobs.ts`

## API surface

- `PUT /identity/rules`
- `GET /identity/rules`
- `GET /identity/lookup`
- `GET /identity/customers/:id`
- `POST /identity/unmerge`
- `POST /identity/merge`
- `GET /identity/merges/:id`
- `GET /identity/merges`
- `POST /identity/conflicts/:id/resolve`
- `GET /identity/conflicts/:id`
- `GET /identity/conflicts`
