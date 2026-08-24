---
cortex-generated: true
title: knowledge-ingestion-rag
tags: [module]
---

# Knowledge ingestion & RAG

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** `packages/api/src/modules/knowledge/,packages/api/src/services/knowledge/`

purpose: per-tenant knowledge sources → extraction → chunking → embeddings → pgvector retrieval; suggestions; scheduled recrawls.
path_prefixes: packages/api/src/modules/knowledge/, packages/api/src/services/knowledge/
key_files: modules/knowledge/{knowledge.service,knowledge.controller,suggestions.service}.ts, services/knowledge/{chunker,indexer,retrieval,reranker,extract,enrich}.ts (chunker/retrieval untracked = in-flight "engine v2"), services/crawler/engine.ts (new crawler), jobs/workers/{knowledge,knowledgeSync}.worker.ts
entrypoints: /api/agents/:agentId/knowledge/* routes; addKnowledgeJob → 'knowledge-processing' queue; repeatable differential recrawl sweep ('knowledge-sync').
responsibilities: PDF/DOCX/HTML/crawler extraction, RecursiveCharacterTextSplitter, Gemini embeddings (1536-dim), DocumentChunk storage, RAG search with injection guards (rag.injection.test.ts), conflict detection (knowledgeConflict.ts), optional push to ElevenLabs KB.
invariants: e2e tier guards slow/huge/wrong-type URL ingestion (4a98dde); embeddings provider auto-fallback (EMBEDDINGS_PROVIDER=auto|gemini).
pitfalls: migration 20260824120000_knowledge_engine_v2 uncommitted together with code — branch ships as a unit or not at all; single-URL ingestion was hardened after prod issues (see sha).
confidence: verified (v2 pieces strongly_inferred)

## Files (14+)

- `packages/api/src/modules/knowledge/knowledge.controller.ts`
- `packages/api/src/modules/knowledge/knowledge.routes.ts`
- `packages/api/src/modules/knowledge/knowledge.schemas.ts`
- `packages/api/src/modules/knowledge/knowledge.service.ts`
- `packages/api/src/modules/knowledge/suggestions.controller.ts`
- `packages/api/src/modules/knowledge/suggestions.service.test.ts`
- `packages/api/src/modules/knowledge/suggestions.service.ts`
- `packages/api/src/services/knowledge/chunker.test.ts`
- `packages/api/src/services/knowledge/chunker.ts`
- `packages/api/src/services/knowledge/enrich.ts`
- `packages/api/src/services/knowledge/extract.ts`
- `packages/api/src/services/knowledge/indexer.ts`
- `packages/api/src/services/knowledge/reranker.ts`
- `packages/api/src/services/knowledge/retrieval.ts`

## API surface

- `POST /:agentId/knowledge/suggestions/:suggestionId/dismiss`
- `POST /:agentId/knowledge/suggestions/:suggestionId/accept`
- `POST /:agentId/knowledge/suggestions/import-from-conversations`
- `GET /:agentId/knowledge/suggestions`
- `POST /:agentId/knowledge/resync-all`
- `POST /:agentId/knowledge/website/confirm`
- `POST /:agentId/knowledge/website/discover`
- `DELETE /:agentId/knowledge/:sourceId`
- `POST /:agentId/knowledge/:sourceId/resync`
- `POST /:agentId/knowledge/urls`
- `POST /:agentId/knowledge/files`
- `GET /:agentId/knowledge`
