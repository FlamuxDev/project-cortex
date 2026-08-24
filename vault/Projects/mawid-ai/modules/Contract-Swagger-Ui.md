---
cortex-generated: true
title: contract-swagger-ui
tags: [module]
---

# Contract & Swagger UI

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `apps/web/public/,docs/`

purpose: machine-checked API documentation without codegen dependency.
path_prefixes: apps/web/public/, docs/
key_files: public/openapi.json (1428 lines, all 59 routes), public/api-docs.html (CDN-loaded Swagger UI), lib/openapi.test.ts (walks app/api/**/route.ts; fails if route+method missing OR spec documents nonexistent route), docs/mobile-api.openapi.yaml (hand-written YAML twin — STALE, still lists deleted endpoints)
confidence: high

