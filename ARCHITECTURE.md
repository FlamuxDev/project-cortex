# Architecture

```
                 Coding Agent / Human
                  │              ▲
        cortex CLI│              │context packets
        MCP stdio │              │impact reports
                  ▼              │
            ┌─────────────────────────┐
            │   Context Selection     │  budget-aware, priority-ordered
            │   Engine                │
            └───┬──────────┬──────────┘
                │          │
   ┌────────────▼───┐  ┌───▼──────────────┐
   │ Hybrid         │  │ Knowledge Layer  │
   │ Retrieval      │  │ memories (FTS)   │
   │ BM25 (FTS5)    │  │ modules/flows    │
   │ + IDF keyword  │  │ decisions        │
   │   overlap      │  │ episodes (empty, │
   │ + memory       │  │  ready schema)   │
   │   anchors      │  └──────────────────┘
   │ + importance   │
   └───────┬────────┘
           │
   ┌───────▼────────┐   ┌──────────────┐   ┌───────────────┐
   │ Code Intel     │   │ Git Intel    │   │ Project Meta  │
   │ symbols/refs/  │   │ commits,     │   │ files, langs, │
   │ routes/tables  │   │ co-change,   │   │ freshness     │
   │ tests mapping  │   │ fix-history  │   │               │
   └────────────────┘   └──────────────┘   └───────────────┘
           └────────────── SQLite (data/cortex.db) ─────────────┘
```

## Components

**Discovery** (`discovery.py`) walks `~/Dev`, skips generated dirs and `pems/` (SSH keys),
resolves nested repos (FARAJ → farj-portfolio), detects manifests/workspaces/kind.

**Extraction** (`extractors.py`) — deterministic parsers:
- TypeScript/TSX/JS/JSX via **tree-sitter**: classes/interfaces/types/enums/functions/components,
  methods, imports, call edges for imported symbols, Express/Fastify/Hono-style `app.get(...)` routes,
  NestJS `@Controller`+`@Get` decorators (incl. bare `@Post()`), drizzle/pgTable entities.
- Python via **stdlib `ast`**: defs/classes with docstrings, imports, calls against known names,
  FastAPI/Flask decorator routes.
- Go via tree-sitter: funcs/methods/structs/interfaces, imports, calls, `http.HandleFunc` routes.
- SQL: tables/views/types/functions + **RLS policies** as first-class symbols. Prisma models.
- Next.js App Router conventions (`app/**/route.ts` exporting GET/POST...) at the indexer level.

**Import resolution** — relative paths, `@/`+`~/` aliases, monorepo suffix matching fallback.
Unresolved imports stay in `refs` with NULL dst_path (used by impact's barrel fallback).

**Indexing** (`indexer.py`) — full or incremental. Incremental diffs content hashes,
re-extracts only changed files, marks intersecting memories stale, appends new git commits,
recomputes importance, rebuilds per-project FTS rows. Freshness is computed **live from git**
at query time (stored head is never trusted).

**Git mining** (`gitmine.py`) — categorized commits (fix/feat/refactor/docs/chore), file→commit
mapping for hotspots/co-change and "past fixes here" warnings.

**Knowledge layer** — delegate-produced deep-analysis reports (one per project, strict schema)
parsed into `memories` (scoped: project/architecture/module/pitfall/history/business_rule/global),
`modules` (path-prefix owned), `flows`, `decisions`. Every memory carries confidence
(`verified|strongly_inferred|inferred|uncertain`), origin (`delegate|curated|generated`),
source-file provenance and `verified_at_commit`.

**Retrieval** (`search.py`, `contextpack.py`) — signals combined:
1. semantic anchors: task-matching module memories cite path prefixes (brace-expanded) → strongest boost
2. IDF-weighted task-keyword hits in file paths (rare terms dominate; guarantee sweep over all paths)
3. normalized BM25 (symbols w/ signatures+docs, file paths, memories)
4. graph: importers/callers/tests/apis/db-entity adjacency
5. static importance (fan-in, entrypoints, route handlers, inverse fix-count)

**Context packets** — sections ordered by fixed priority (header/module/files/symbols/read-first/
callers/impact/tests/rules/db/history/warnings/knowledge), assembled under a char budget
(4 chars ≈ 1 token). Cross-project mode (`--all`, auto-triggered by cues like "across projects")
interleaves evidence round-robin per project so no repo dominates. An **evidence-warning
guardrail** lists task terms absent from the project instead of letting partial matches pose as answers.

**Impact analysis** — direct dependents (callers+importers+barrel-name matches), BFS indirect
dependents, mapped tests, served API routes, touched DB entities, risk level + reasons,
recent history and past fixes on the exact files.

## Deliberate decisions

| Decision | Why |
|---|---|
| Python stdlib-first, single venv dep set | maintainable; tree-sitter only real dependency |
| SQLite + FTS5 over a vector DB | measured: lexical+graph+memory beats need for embeddings at this corpus size; zero service management |
| No embeddings (yet) | retrieval eval hit 100% without them; revisit if eval regresses |
| Zero-dep hand-rolled MCP server (~250 lines) | avoids SDK churn; protocol surface needed is tiny |
| Live git checks for freshness | stored HEAD lies after every commit |
| Delegate reports are curated inputs, DB is truth | reports regenerate independently of code indexes |
