# Architecture (public overview)

A condensed tour of the system. Honest caveats live in [`LIMITATIONS.md`](LIMITATIONS.md); measured numbers in [`BENCHMARKS.md`](BENCHMARKS.md).

## Components

```
                 Coding Agent / Human
                  │              ▲
        cortex CLI│              │context packets (budgeted)
        MCP stdio │              │impact reports
                  ▼              │
            ┌─────────────────────────┐
            │ Live Guard + Context    │  versioned working-tree snapshot,
            │ Selection + Preflight   │  packets / architecture / diff risk
            └───┬──────────┬──────────┘
                │          │
   ┌────────────▼───┐  ┌───▼──────────────┐
   │ Hybrid         │  │ Knowledge Layer  │
   │ Retrieval      │  │ memories (FTS)   │
   │ BM25 (FTS5)    │  │ modules / flows  │
   │ + IDF keyword  │  │ decisions        │
   │   overlap      │  │ episodes         │
   │ + memory       │  └──────────────────┘
   │   anchors      │
   │ + importance   │
   └───────┬────────┘
           │
   ┌───────▼────────┐   ┌──────────────┐   ┌───────────────┐
   │ Code Intel     │   │ Git Intel    │   │ Task Memory   │
   │ symbols/refs/  │   │ commits,     │   │ sessions →    │
   │ routes/tables  │   │ co-change,   │   │ episodes →    │
   │ tests mapping  │   │ fix-history  │   │ lessons       │
   └────────────────┘   └──────────────┘   └───────────────┘
           └────────────── SQLite (~/.cortex or CORTEX_DATA_DIR) ─────────────┘
```

**Discovery** walks configured roots (`cortex init`), skips generated dirs and key material, resolves nested repos, detects manifests/frameworks/kind. Projects need ≥3 code files.

**Extraction** is deterministic — no models in the loop:
- TypeScript/TSX/JS/JSX via tree-sitter: classes/interfaces/types/enums/functions/components, methods, imports, call edges for imported symbols, Express/Fastify/Hono-style routes, NestJS decorators, drizzle/pgTable entities.
- Python via stdlib `ast`: defs/classes with docstrings, imports, calls, FastAPI/Flask routes.
- Go via tree-sitter: funcs/methods/structs/interfaces, imports, calls, `http.HandleFunc` routes.
- Regex extractors: SQL tables/views/types/functions + RLS policies as first-class symbols; Prisma models.
- Next.js App Router conventions (`app/**/route.ts`) resolved at the indexer level.
- Import resolution: relative paths, `@/`+`~/` aliases, monorepo suffix fallback; unresolved imports stay in `refs` and feed impact's barrel-reexport fallback.

**Indexing** — full or incremental. Incremental diffs sha1 content hashes, re-extracts only changed files, rebuilds changed test mappings, marks intersecting memories stale, appends new git commits, recomputes importance, and replaces per-project FTS rows. Orphan FTS rows are pruned so removed symbols cannot leak into later searches. Versioned index-format markers trigger a one-time derived-data repair; clean repositories do not need a cold re-parse after upgrading.

**Live Context Guard** fingerprints HEAD plus the contents of dirty indexable paths
(or all indexable files outside Git). Before task/context/architecture/preflight calls,
it skips work when the marker matches, otherwise runs an incremental refresh under an
atomic per-project lock. Locks recover immediately when their owner process dies and
also have a conservative stale timeout. The marker is recorded only if the worktree did
not change during indexing.

**Repository intelligence** derives an architecture snapshot from indexed files and
graph edges. Git preflight reads staged, unstaged, untracked, deleted, and renamed paths
against a validated base, preserves pre-refresh evidence for removals, then maps the
diff to callers, API/data surfaces, risk, and tests.

**Git mining** categorizes commits (fix/feat/refactor/docs/chore), builds file→commit mappings for hotspots, co-change, and "past fixes here" warnings.

**Knowledge layer** — curated/delegate-produced reports parsed into `memories` (scopes: project/architecture/module/pitfall/history/business_rule/global), `modules`, `flows`, `decisions`. Every memory carries confidence, origin, source-file provenance, and the commit it was verified at.

## Ranking signals (context packets)

```
score = 10 * kw_idf_score/7   task keywords in file paths, IDF-weighted (rare terms dominate;
                              guarantee sweep over ALL paths, not just the FTS pool)
      + 8   memory anchor     path prefixes cited by task-matching module memories
                              (strongest single signal; brace-expanded prefixes)
      + 4 * normalized bm25   over symbols w/ signatures+docs, file paths, memories
                              (normalized because raw magnitudes varied 10x across corpora)
      + .02 static importance fan-in, entrypoints, route handlers, inverse fix-count
```

Keyword-IDF dominates because it is task-specific; this mix is what took the retrieval eval from 18/20 (plain BM25) to 20/20. Sections are assembled in fixed priority order (header/module/files/symbols → callers/impact/tests/rules/db/history/warnings/knowledge) under a char budget (4 chars ≈ 1 token). Cross-project queries interleave evidence round-robin per project so no repo dominates.

An **existence guardrail**: if task terms appear nowhere in the project's indexed paths/symbols, the packet emits `⚠ EVIDENCE WARNING` instead of letting partial matches pose as answers.

## Confidence model

```
verified > strongly_inferred > inferred > uncertain
```

Deterministic indexes (symbols/routes/tables/commits) are facts. Prose knowledge carries an explicit confidence tag plus provenance (`source_files_json`, `verified_at_commit`). Episodes gain confidence from evidence: commit + lessons → `verified`. Cortex never invents claims — agents pass validated lessons; Cortex attaches deterministic evidence.

## Freshness model

Nothing trusts stored state. Every packet/query recomputes live:

- current `git rev-parse HEAD` vs `indexed_commit`
- commit-count distance since the indexed commit
- dirty-file count via `git status --porcelain`
- exact fingerprint of dirty indexable paths, checked against the versioned index marker

Memories whose evidence files changed after ingest are flagged `[STALE]`; packets state
staleness in their header instead of pretending to be current. A dirty worktree is never
labeled clean even when its code is fully indexed. Concurrent edits during refresh yield
`unstable`, never a false current marker.

## Storage schema summary

SQLite at `CORTEX_DATA_DIR` (default `~/.cortex/data/cortex.db`), WAL mode, migrations applied automatically on connect.

| Group | Tables |
|---|---|
| Code intel | `files` (content hash, importance), `symbols` (kind, signature†, line range), `refs` (import/call/use edges), `apis`, `db_entities`, `tests` |
| Knowledge | `memories`† (scope/confidence/stale), `modules`, `module_files`, `flows`, `decisions` |
| History | `commits`, `commit_files` (category-mined) |
| Learning loop | `task_sessions`, `episodes` |
| Search | `fts_symbols`, `fts_files`, `fts_memories` (FTS5, rebuilt per-project on index) |

† secret-redacted before insert (`langs.redact`). Env var *names* may be stored; values never are.

## Deliberately NOT included (and when that changes)

| Excluded | Why | Revisit trigger |
|---|---|---|
| Embeddings / vector DB | Measured: IDF keyword overlap + memory anchors + normalization fixed what plain BM25 got wrong; eval hit 20/20 without vectors. No model dependency, no update pipeline, explainable ranking. | Eval score regresses, or repos >50k files |
| LSP servers | Cortex needs retrieval-grade intelligence ("which files/symbols/tests matter for this task"), not IDE-grade rename precision. tree-sitter + refs graph starts in milliseconds with zero per-language daemons. The extractor interface is pluggable if reference-quality ever demands it. | A use case needs rename/refactor-grade accuracy |
| Daemons, cloud sync, accounts | Local-first by design: one SQLite file, one stdio process. | Never planned |

See also: [`LIMITATIONS.md`](LIMITATIONS.md).
