---
cortex-generated: true
title: studio-versions-templates-a-b-ai-copilot-personalization
tags: [module]
---

# studio, versions, templates, A/B, AI copilot, personalization

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `packages/core/src/content,packages/adapters/ai-gemini`

purpose: channel content per campaign version; immutable append-only versions; variant allocation; AI suggestions with structural human-in-the-loop; {{token}} rendering.
path_prefixes: packages/core/src/content, packages/adapters/ai-gemini
key_files: packages/core/src/content/copilot.ts, personalization.ts, abTest.ts, preview.ts, repository.ts; packages/adapters/ai-gemini/src/prompt.ts
entrypoints: campaign sub-routes …/content*, /variants, /allocations, /ab-test, /preview, /ai/suggest|accept; renderContent() inside dispatch()
responsibilities: version history + restore; template application; A/B fingerprint where each field matters individually (commit 10f7a0d); prompt-injection boundary: instructions ONLY from closed AiTask set into systemInstruction, user brief travels as JSON data (prompt.ts).
invariants: `suggest()` writes nothing; nothing applies model output without a separate audited accept taking text as argument (copilot.ts — property of module shape, not a removable check); content_version immutability enforced by DB trigger (migration 0016/0020); missing-fallback token blanks rather than crashes at send time (submission-time blocker instead).
confidence: verified

## Files (11+)

- `packages/adapters/ai-gemini/src/index.ts`
- `packages/adapters/ai-gemini/src/prompt.ts`
- `packages/adapters/ai-gemini/src/prompt.unit.test.ts`
- `packages/core/src/content/abTest.ts`
- `packages/core/src/content/abTest.unit.test.ts`
- `packages/core/src/content/copilot.ts`
- `packages/core/src/content/copilot.unit.test.ts`
- `packages/core/src/content/personalization.ts`
- `packages/core/src/content/personalization.unit.test.ts`
- `packages/core/src/content/preview.ts`
- `packages/core/src/content/repository.ts`

## API surface

- `GET acceptSuggestion`
- `GET suggestContent`
