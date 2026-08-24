---
cortex-generated: true
title: model-transcription-rag
tags: [module]
---

# Model, transcription, RAG

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `packages/ai/src/infrastructure/ai/`

purpose: sole Gemini build site; voice transcription; org knowledge embeddings.
path_prefixes: packages/ai/src/infrastructure/ai/
key_files: gemini.ts (AGENT_MODEL_SETTINGS — the only place model settings may change), transcription.ts, rag/retrieve.ts + sync.ts (organization_knowledge_chunks, 768-dim vector search)
invariants: build the model nowhere else; do not re-enable thinking without raising maxOutputTokens far above reasoning ceiling
confidence: high

## Files (4+)

- `packages/ai/src/infrastructure/ai/gemini.ts`
- `packages/ai/src/infrastructure/ai/rag/retrieve.ts`
- `packages/ai/src/infrastructure/ai/rag/sync.ts`
- `packages/ai/src/infrastructure/ai/transcription.ts`
