---
cortex-generated: true
title: settings-message-repository
tags: [module]
---

# Settings + message repository

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `packages/backend/src/infrastructure/`

purpose: platform flag resolution and the centralized history-read invariant.
path_prefixes: packages/backend/src/infrastructure/
key_files: platform/settings.ts (`isPaymentsEnabled`, `getPlatformCronSecret`), repositories/message-repository.ts (loads RECENT history in correct order — the prod-outage invariant from bef6b1d lives here)
invariants: never read conversation history raw/oldest-first anywhere else
confidence: high

## Files (2+)

- `packages/backend/src/infrastructure/platform/settings.ts`
- `packages/backend/src/infrastructure/repositories/message-repository.ts`
