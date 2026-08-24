---
cortex-generated: true
title: append-only-audit-trail
tags: [module]
---

# append-only audit trail

**Project:** [[cvm]] | **Confidence:** verified | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/audit/`

purpose: audit_event append-only at DB level; searchable; correlation-joined; /audit/correlation/{id} shows everything in one action.
path_prefixes: packages/modules/src/audit/
key_files: audit/index.ts (recordAudit), http/routes.ts
entrypoints: auditRoutes
invariants: mutating routes must declare audited/auditExempt at boot (pipeline guard); security denials recorded in ACTOR'S tenant.
confidence: verified

## Files (5+)

- `packages/modules/src/audit/application/record.ts`
- `packages/modules/src/audit/application/search.ts`
- `packages/modules/src/audit/domain/types.ts`
- `packages/modules/src/audit/http/routes.ts`
- `packages/modules/src/audit/index.ts`

## API surface

- `GET /audit/correlation/:correlationId`
- `GET /audit`
