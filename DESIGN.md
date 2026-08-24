# Design Notes

Decisions made while building, with reasoning — the "why" behind ARCHITECTURE.

## Why not Serena / LSP?

Serena brings LSP-grade symbol intelligence but demands per-language language servers running,
project-scoped servers, and a heavier runtime. Cortex needs **retrieval-grade** intelligence
(find the file/symbol/callers that matter for a task), not IDE-grade rename-refactor precision.
tree-sitter + a SQLite refs graph covers the retrieval need deterministically and starts in
milliseconds. The `refs` graph is honest about its limits (see KNOWN_LIMITATIONS) and the
extractor interface is pluggable if LSP precision is ever needed (`find_references` quality).

## Why no embeddings/GraphRAG?

Measured during the build: BM25-over-paths alone mis-ranked noisy single-term matches, but the
fixes that worked were **IDF keyword overlap, memory-anchored boosting, and per-project
round-robin** — all deterministic and explainable. After those, the 20-question retrieval eval
hits 100% and adversarial scenarios improved from 7-pass to substantially better without any
vector index. Embeddings would add a model dependency, an update pipeline and opaque failures
for marginal gain at 14 repos / ~69k symbols. Revisit trigger: eval score drop or >50k-file repos.

## Ranking signal weights (context packets)

```
score = 10 * kw_idf_score/7   (task keywords in path, IDF-weighted; guarantee sweep)
      + 8  memory-anchor hit  (module path_prefixes cited by task-matching memories)
      + 4  normalized bm25    (per result set)
      + .02 importance        (fan-in, entrypoint, routes, inverse fix count)
```

Keyword-IDF dominates because it is task-specific; bm25 is normalized because raw magnitudes
varied 10x across corpora and drowned everything else (a real bug found during eval tuning).

## Freshness model

Every query recomputes: live HEAD vs `indexed_commit`, commit-count distance via dates, live
`git status --porcelain` count. Stale memories (evidence files touched by later changes) are
flagged `[STALE]` in packets. Nothing trusts stored state.

## Confidence model

`verified` (delegate read the code directly / deterministic extraction) >
`strongly_inferred` (multiple consistent signals) > `inferred` > `uncertain`.
Deterministic indexes (symbols/routes/tables) are facts; prose knowledge carries confidence +
provenance (`source_files_json`, `verified_at_commit`). The hallucination audit measured 83%
fully-verified claims, zero fabricated artifacts (see HALLUCINATION_AUDIT.md).

## Secrets posture

Redaction runs on every signature/doc/subject before insert (`langs.redact`). `pems/` is
excluded at discovery. Env var *names* may be stored; values never are. See SECURITY_REVIEW.md.

## Generated vs curated vault notes

Vault generator stamps frontmatter `cortex-generated: true` and refuses to overwrite files
without it. Human edits to vault notes survive regeneration.

## Incremental indexing contract

File identity = sha1(content). Update = hash-diff vs DB → re-extract changed only → delete+
insert their rows → mark intersecting memories stale → append new commits → recompute derived
scores for the project → rebuild that project's FTS rows. Cold index ~14 min (mythos ≈ 13 min
of it); incremental runs in seconds.
