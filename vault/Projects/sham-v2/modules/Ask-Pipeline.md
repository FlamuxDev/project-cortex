---
cortex-generated: true
title: ask-pipeline
tags: [module]
---

# ask() pipeline

**Project:** [[sham-v2]] | **Confidence:** inferred | **verified@** `71fbe7ede70c`
**Owns:** `src/agent/index.js,src/agent/prompt.js,src/agent/gemini.js`

purpose: one path from any channel's question to a grounded Arabic answer.
path_prefixes: src/agent/index.js, src/agent/prompt.js, src/agent/gemini.js
key_files: src/agent/index.js:350-586 (`ask()` main loop), index.js:303-334 (`plan()` structured call, temperature 0, maxOutputTokens 8192), index.js:442-565 (repair loop: max 3 deterministic repairs, provider 504/429 retries don't consume repair rounds), index.js:126-133 (LRU answer cache keyed per generation)
entrypoints: `ask(question, options)` — called by HTTP controller, WhatsApp worker, voice channel
responsibilities: scope decision, SQL generation w/ full-schema prompt, zero-row review round, humanize pass over the same rows (fallback to deterministic text if model fails), time-budget management (deadline + remaining() guards everywhere)
invariants: model never authors facts; EMPTY(verified_zero) survives later failures (index.js:567-572); cache key includes activeGeneration() so stale-generation answers can't leak (index.js:384)
pitfalls: many narrow regex intent-detectors hardcoded here (reviewer privacy, teacher-affiliation count, near-me intent — index.js:47-66,136) — each is product logic living in the pipeline file
confidence: high

## Files (3+)

- `src/agent/gemini.js`
- `src/agent/index.js`
- `src/agent/prompt.js`
