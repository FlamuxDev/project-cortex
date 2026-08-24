---
cortex-generated: true
title: catalog-generations-semantic-layer
tags: [module]
---

# catalog generations & semantic layer

**Project:** [[sham-v2]] | **Confidence:** inferred | **verified@** `71fbe7ede70c`
**Owns:** `src/db/{catalog,pointer,schema,semantics,mirror,build}.js`

purpose: build immutable readonly SQLite catalogs from PGDMP backups; describe every column to the model.
path_prefixes: src/db/{catalog,pointer,schema,semantics,mirror,build}.js
key_files: catalog.js:36-56 (serving vs build mode; `query_only=ON`; explicit startup error not silent empty DB); semantics.js:14-60 (SENSITIVITY policy public/on_request/hidden/never + NEVER_COPY_COLUMNS physical exclusion of passwords/tokens/DOB etc.); schema.js (auto-profiling: types, JSON keys, enumerated values, row counts — feeds the 64KB prompt)
entrypoints: `npm run sync` (src/db/build.js); pointer swap via active.json
responsibilities: atomic generation swap triggers graceful restart when CATALOG_RESTART_ON_ACTIVATION set (src/server.js:62-67); derived tables institutions/teachers/posts created in build mode (catalog.js:79-142)
invariants: serving DB never written (readonly+query_only); internal tables marked exposure=internal aren't copied at all (semantics.js:20-21)
pitfalls: pg_restore required to build new generations (ships prebuilt so check works offline); don't touch storage/catalogs manually (AGENTS.md)
confidence: high

## Files (5+)

- `scripts/schema.js`
- `src/db/mirror.js`
- `src/db/pointer.js`
- `src/db/schema.js`
- `src/db/semantics.js`

## API surface

- `GET teacher_more_info`
- `GET users`
