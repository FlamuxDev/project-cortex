---
cortex-generated: true
title: test-suites-verification-gates
tags: [module]
---

# Test Suites & Verification Gates

**Project:** [[mushagil]] | **Confidence:** verified | **verified@** `638838aad84d`
**Owns:** `packages/testing,quality/,scripts/`

purpose: suite registry routing, ephemeral DB harness, anti-cheating guards.
path_prefixes: packages/testing, quality/, scripts/
key_files: quality/suite-registry.json (14 suites w/ requiredFrom module gating), scripts/run-suite.mjs (SUITE_EMPTY if a DONE-module suite matches zero files — tamper-tested), scripts/verify-suites.mjs, packages/database/tests/support/ephemeral-db.ts, vitest.config.ts (single root config)
entrypoints: pnpm test:* / verify:* root commands (package.json)
responsibilities: suites become mandatory only when their owning module is DONE in MODULES.md; unit=no DB/network, integration=real ephemeral Postgres+Redis.
invariants: MODULES.md §20 anti-cheat: weakening assertions/skipping tests/fake success invalidates green.
confidence: verified

