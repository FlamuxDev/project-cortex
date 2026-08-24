---
cortex-generated: true
title: validated-environment
tags: [module]
---

# validated environment

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `packages/config`

purpose: the ONLY reader of process.env; zod-validated, fails boot loudly.
path_prefixes: packages/config
key_files: packages/config/src/index.ts
entrypoints: getConfig() called by apps/*/src/container.ts and server mains
responsibilities: parse env once; missing/invalid ⇒ exit non-zero listing ALL problems.
invariants: NODE_ENV required with NO default (a defaulted deploy once booted fail-open — token echo + non-Secure cookie, commit 578b127); RESEND_API_KEY+EMAIL_FROM required together or fake email stays live; RESEND_WEBHOOK_SECRET absent ⇒ inbound webhook refuses everything.
pitfalls: adding env reads anywhere else breaks SEC-004 and the audit:security gate.
confidence: verified

