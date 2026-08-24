---
cortex-generated: true
title: query-validation-sandboxed-execution
tags: [module]
---

# query validation & sandboxed execution

**Project:** [[sham-v2]] | **Confidence:** inferred | **verified@** `71fbe7ede70c`
**Owns:** `src/agent/guard.js,src/agent/execute.js,src/agent/worker.js`

purpose: reject unsafe/wrong SQL before execution; run it isolated.
path_prefixes: src/agent/guard.js, src/agent/execute.js, src/agent/worker.js
key_files: guard.js:317-447 (`validateSql` — 6 layers: literal stripping/keyword ban → SQLite prepare → stmt.readonly verdict → output-column source attribution for sensitive fields → FROM/JOIN table allowlist → EXPLAIN QUERY PLAN cost cap of 1e7 estimated row visits); guard.js:66-82 (bans non-ASCII literal comparisons — Arabic hamza variants silently return 0 rows; forces `like_ar()`); execute.js:25-74 (per-query Worker thread w/ resource limits, timeout kills without waiting on terminate, leakedWorkers counter)
entrypoints: `runSql(sql, {allowContact,...})` (execute.js:130-183) — the ONLY execution door
responsibilities: contact columns blocked unless user explicitly asked (`allowContact`); entity-name-without-id rule so UI can deep-link rows (guard.js:396-407); LIMIT injection; cell truncation; redacted SQL logging
invariants: every query passes guard.js (AGENTS.md constant); sensitive columns physically absent from the file anyway (semantics NEVER_COPY_COLUMNS) — guard is defense-in-depth layer 2
pitfalls: heavy regex-on-SQL layers are bypassable in principle (acknowledged in guard.js header: "the parser being SQLite itself" is the real wall); leaked workers metric is the ops alarm (execute.js:185-186)
confidence: high

## Files (3+)

- `src/agent/execute.js`
- `src/agent/guard.js`
- `src/agent/worker.js`
