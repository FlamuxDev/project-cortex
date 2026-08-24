---
cortex-generated: true
title: cloudfront-function-local-twin
tags: [module]
---

# CloudFront function & local twin

**Project:** [[umbrellaprime]] | **Confidence:** inferred | **verified@** `b56420dad197`
**Owns:** `infra/,scripts/static-server.mjs`

purpose: make clean URLs work on exact-key S3; reproduce identically in tests.
path_prefixes: infra/, scripts/static-server.mjs
key_files: infra/cloudfront-function.js:9-20 (append index.html for dir URIs and dot-less paths), cloudfront-function.test.mjs (node --test coverage of rewrite logic)
entrypoints: attached viewer-request on distribution; scripts invoked by npm start / playwright webServer
responsibilities: parity between prod and test URL resolution
invariants: trailingSlash:true in next.config.ts is what makes the file layout match this scheme
confidence: high

## Files (4+)

- `infra/cloudfront-function.js`
- `infra/cloudfront-function.mjs`
- `infra/cloudfront-function.test.mjs`
- `scripts/static-server.mjs`
