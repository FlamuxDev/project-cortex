---
cortex-generated: true
title: email-handler
tags: [module]
---

# email handler

**Project:** [[umbrellaprime]] | **Confidence:** inferred | **verified@** `b56420dad197`
**Owns:** `lambda/contact/index.mjs (+ index.test.mjs,function.zip committed)`

purpose: validate + throttle + email submissions via Resend.
path_prefixes: lambda/contact/index.mjs (+ index.test.mjs, function.zip committed)
key_files: index.mjs:8-22 (per-container in-memory rate limit 5/10min — explicitly marked ponytail ceiling with DynamoDB upgrade path), index.mjs:27-34 (loose English schema; full localized validation already ran client-side), index.mjs:57-59 (CORS belongs to Function URL config, NOT response headers — duplicates break browsers), index.mjs:86-88 (not-configured is 200 with status)
entrypoints: Function URL (POST only)
responsibilities: reply-to set to submitter; base64 body handling
invariants: no secrets in code; RESEND_API_KEY etc. set on the function itself
pitfalls: rate limit warms per container only — not a global guarantee
confidence: high

