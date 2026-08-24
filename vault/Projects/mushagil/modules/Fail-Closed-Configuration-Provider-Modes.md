---
cortex-generated: true
title: fail-closed-configuration-provider-modes
tags: [module]
---

# Fail-Closed Configuration & Provider Modes

**Project:** [[mushagil]] | **Confidence:** verified | **verified@** `638838aad84d`
**Owns:** `packages/config/src`

purpose: validated env schema + secret handling + production fake/sandbox refusal.
path_prefixes: packages/config/src
key_files: src/env-schema.ts, src/config.ts, src/provider-mode.ts, src/secret.ts, src/load-env-file.ts
entrypoints: getConfig() called at boot of api/worker
responsibilities: single zod schema for all MUSHAGIL_*/DATABASE_*/REDIS_* vars; Secret type prevents accidental leakage; load order .env.example → .env.test.local → process env.
invariants: assertProviderModesAllowed throws PROVIDER_MODE_FORBIDDEN in production for fake mode or un-allow-listed sandbox mode.
pitfalls: defaults for all five provider modes are "fake" — safe locally, fatal in prod by design; REDIS_SOCKET_PATH unix-socket path is a sandbox-only alternative to TCP (portability trap documented in .env.example).
confidence: verified

