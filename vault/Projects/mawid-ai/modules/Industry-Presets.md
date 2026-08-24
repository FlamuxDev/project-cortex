---
cortex-generated: true
title: industry-presets
tags: [module]
---

# Industry presets

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `packages/ai/src/industry/`

purpose: seed services/catalog per business vertical chosen at signup.
path_prefixes: packages/ai/src/industry/
key_files: seed-catalog.ts, seed-industry-preset.ts, appointment-presets.ts
notes: industry is collected once at signup (`/api/auth/register` seeds it), editable in Settings; deliberately NOT a setup-wizard step (deleted step, do not reintroduce)
confidence: high

## Files (3+)

- `packages/ai/src/industry/appointment-presets.ts`
- `packages/ai/src/industry/seed-catalog.ts`
- `packages/ai/src/industry/seed-industry-preset.ts`
