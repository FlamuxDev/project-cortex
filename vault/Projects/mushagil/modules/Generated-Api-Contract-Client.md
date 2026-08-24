---
cortex-generated: true
title: generated-api-contract-client
tags: [module]
---

# Generated API Contract & Client

**Project:** [[mushagil]] | **Confidence:** verified | **verified@** `638838aad84d`
**Owns:** `packages/contracts,apps/api/src/openapi`

purpose: committed openapi.json + generated types/client; drift gate.
path_prefixes: packages/contracts, apps/api/src/openapi
key_files: openapi/openapi.json, src/generated/api.d.ts, apps/api/src/openapi/generate-openapi.ts, scripts/verify-openapi.mjs
entrypoints: web imports createAuthenticatedApiClient types; verify gate in CI.
responsibilities: single source of HTTP truth; tamper-tested drift gate (mutating openapi.json fails exit 1, M01 evidence).
invariants: live app must match committed document exactly.
pitfalls: regeneration is part of bootstrap; forgetting to regenerate after adding routes fails verify:openapi (intentionally).
confidence: verified

