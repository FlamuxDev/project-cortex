---
cortex-generated: true
title: shared-frontend-libraries
tags: [module]
---

# Shared frontend libraries

**Project:** [[telvora]] | **Confidence:** inferred | **verified@** `7423f040ed46`
**Owns:** `packages/{ui,design-tokens,i18n,contracts}/src`

purpose: @telvora/ui (27 components incl. DecisionTrace, AuditLogRow, ConsentStatusPill), design-tokens (tokens.css), i18n (en.ts/ar.ts dictionaries), contracts (generated route list + OpenAPI)
path_prefixes: packages/{ui,design-tokens,i18n,contracts}/src
key_files: packages/contracts/src/core-api-routes.ts (generated), openapi/{core-api,ml}.openapi.json
confidence: strongly_inferred (ui/i18n internals not exhaustively read)

## Files (3+)

- `packages/i18n/src/ar.ts`
- `packages/i18n/src/en.ts`
- `packages/i18n/src/index.ts`
