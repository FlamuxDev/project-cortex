---
cortex-generated: true
title: knowledge-rag
tags: [module]
---

# knowledge / RAG

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Ingestion: sources of type file/url/text/faq/crawler; upload goes to S3 (`utils/s3.ts`), then `addKnowledgeJob` → `knowledge.worker.ts`: extract (pdf-parse / mammoth DOCX→HTML→Markdown / cheerio HTML / text, `knowledge.worker.ts:32-80`), safeFetch for URLs (`services/security/urlGuard.ts` SSRF guard), structural Markdown chunking with section breadcrumbs (`services/knowledge/chunker.ts`), optional LLM contextual enrichment (`enrich.ts`), batched embeddings (8 in flight, `indexer.ts:69-88`), atomic chunk swap in one transaction (`indexer.ts:90-108`), optional cross-source conflict detection (`ai/knowledgeConflict.ts`), optional ElevenLabs KB sync.
- Crawls: `KnowledgeSource.config` holds maxDepth/maxPages/schedule/patterns/renderMode ('static'|'auto'|'browser' via puppeteer); `KnowledgePage` is the unit of change detection (contentHash skip); `KnowledgeSyncRun` audits each run; differential recrawls driven by `nextSyncAt`/`syncIntervalHours` + `knowledge-sync` queue sweeper (`jobs/workers/knowledgeSync.worker.ts`, schema 265-354).
- Retrieval: query embedding with `RETRIEVAL_QUERY` task type → `hybridSearch`: three SQL CTEs (pgvector cosine dense LIMIT 40, tsvector 'simple', tsvector 'arabic') fused by Reciprocal Rank Fusion k=60, all arms join-scoped to `agent_id AND status='ready'` (`services/knowledge/retrieval.ts:37-115`) → optional rerank (`reranker.ts`, provider from KNOWLEDGE_RERANKER env) → ±1 (±2 for multi-question queries) neighbor expansion (`retrieval.ts:129-171`, multi-part heuristic `rag.ts:104-106`).
- Self-improvement: analysis worker mines FAQ/gap suggestions into `KnowledgeSuggestion` deduped by normalized questionKey (`analysis.worker.ts:184-207`, `suggestions.service.ts`).
- Embeddings service: Gemini-only REST call pinning `outputDimensionality=1536`, transient-error retry w/ jittered backoff, circuit breaker keyed by provider+API-key-hash so one tenant's 429 doesn't open the breaker for everyone (`services/ai/embeddings.ts:20-238`).

