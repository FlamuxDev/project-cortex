# Build Report — Project Cortex v0.1

**Built:** 2026-08-24 → 2026-08-25 · **Location:** `/home/aboud/project-cortex`

## What was built

A permanent, local-first engineering brain covering every meaningful repository under
`~/Dev`: deterministic code intelligence (tree-sitter AST, import/call graph, routes, DB
entities, test mapping, git mining) fused with a curated semantic layer (delegate-produced
deep analyses ingested as provenance-tracked memories), served through a budget-aware
context-packet engine, impact analysis, a zero-dependency MCP server, a CLI, and an
Obsidian vault.

## Final numbers

| Metric | Count |
|---|---|
| Projects discovered / indexed | 14 / 14 |
| Files indexed | 6,545 |
| Symbols indexed | 68,370 |
| Ref edges (imports + calls) | 197,437 (6,028 imports resolved to files) |
| Modules with memories | 166 (3,985 file ownership links) |
| Flows mapped | 77 |
| API routes | 2,502 (2,386 server-side, direction-tagged) |
| DB entities | 1,116 (+ 186 RLS policies as first-class symbols) |
| Tests indexed / target-mapped | 1,944 / 749 |
| Memories | 288 (278 project + 10 global cross-project principles/pitfalls) |
| Decisions extracted | 126 |
| Git commits mined | 1,218 (categorized; per-file mapping for hotspots/warnings) |
| Delegates used | 17 (14 deep-analysis + 1 adversarial audit + 1 hallucination audit + batched smalls) |

## Architecture chosen

Python 3.13 stdlib-first single package; tree-sitter (TS/TSX/JS/Go) + stdlib `ast` (Python)
+ regex (SQL/prisma); SQLite + FTS5 storage; hand-rolled MCP over stdio; generated Obsidian
vault. No embeddings, no daemons, no cloud. Rationale in ARCHITECTURE.md/DESIGN.md.

## Validation performed

| Check | Result |
|---|---|
| Unit/integration tests (`unittest`, fixture repo w/ git) | **18/18 pass** — discovery, extractors (ts/nestjs/py/go/sql), pipeline, import resolution, test mapping, RLS capture, context packet, impact, incremental update, stale flagging, MCP protocol |
| Retrieval evaluation (20 tasks, 14 projects) | **20/20** packets contain ground truth · p50 latency 0.02s · details in RETRIEVAL_EVALUATION.md |
| Token efficiency benchmark | **~94–95% median reduction** in bytes-to-target vs simulated unaided exploration · TOKEN_EFFICIENCY_BENCHMARK.md |
| Hallucination audit (independent delegate, 54 checks, 12 projects) | **45 verified / 4 incorrect / 3 obsolete / 2 unsupported · 0 fabricated artifacts** · all cited SHAs/tables/symbols exist · 5 architectural invariants confirmed in actual code · HALLUCINATION_AUDIT.md |
| Adversarial audit (independent delegate) | pre-fix 9 FAILs found (cross-project routing, confident garbage on nonexistent features, stale freshness, impact barrels, Arabic split-brain) → all fixed: live-git freshness, EVIDENCE-WARNING guardrail, cross-project round-robin retrieval, barrel fallback in impact, AR→EN glossary · ADVERSARIAL_AUDIT.md |

## Safety record

Projects were treated read-only throughout: no source modifications, no formatting, no
commits in project repos, no dependency changes. `~/Dev/pems` (SSH keys) excluded from
indexing entirely. Secret redaction applied at every insert path and covered by tests.

## How to operate daily

```bash
cortex context "<task>"            # start any task here
cortex impact "<file-or-feature>"  # before editing
cortex update                      # after pulling/committing (incremental, seconds)
cortex status <project>            # freshness & counts
cortex doctor                      # health check
cortex serve                       # MCP for coding agents
```

Full rebuild-from-nothing is documented in README.md (≈15 min cold).

## Honest state

The friendly eval is 20/20 but was authored in-process; the two independent audits are the
real quality evidence and they drove material fixes. Remaining weaknesses — approximate
symbol references through barrels, lexical-only cross-project ranking, glossary-based Arabic,
unfed episodes table — are enumerated in KNOWN_LIMITATIONS.md with upgrade paths.
