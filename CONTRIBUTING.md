# Contributing to Project Cortex

Thanks for helping build the engineering brain. This doc covers the rules of the road and maps for the two most common contributions: new language extractors and new MCP tools.

## Ground rules

- **Conventional commits.** `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:` — e.g. `feat(extractors): add Rust struct extraction`.
- **Python stdlib-first.** The only sanctioned runtime dependencies are tree-sitter and its grammars. Anything else needs a strong justification in the PR description.
- **Deterministic only.** No model calls, no network access, no nondeterministic ordering anywhere in the index/retrieve path. Same input → same index → same packet.
- **Secrets never land.** Any new persisted text field (signatures, docs, subjects, bodies) must pass through `cortex.langs.redact` before insert.
- **Honest benchmarks.** If you touch retrieval or packets, add focused public fixture tests and describe the expected ranking change. Maintainers rerun the private-repository eval set before release; reported numbers must stay labeled measured vs simulated.

## Every PR

1. Fork, branch, make your change.
2. Run the full suite:
   ```bash
   python -m unittest discover tests
   ruff check --select F src tests
   ```
   All tests must pass. Tests use throwaway fixture repos; they don't touch a real index.
3. Keep diffs focused — one logical change per PR.
4. Update the relevant doc(s) if you change behavior (`README.md`, `docs/MCP.md`, `ARCHITECTURE.md`).

PRs should state what changed, why, and how you verified it.

## Adding an extractor / language

Extractors live in `src/cortex/extractors.py`. Each language contributes:

1. A parser (tree-sitter grammar if one exists, else stdlib/regex — Python uses `ast`, SQL/Prisma use regex).
2. Symbol extraction → rows for `symbols` (name, kind, parent, line range, signature, exported).
3. Import + call edges → `refs` (resolve what you can; unresolved imports stay with NULL `dst_path` and are handled gracefully downstream).
4. Framework routes if applicable (Express/Fastify/Hono/NestJS/FastAPI/Flask/Gin-style) → `apis`.
5. File-type detection in `src/cortex/langs.py` (`is_code`, extension mapping).
6. Test-file heuristics so test mapping works (see `tests` table population).

Checklist:

- [ ] Grammar added to `pyproject.toml` dependencies (tree-sitter-<lang>)
- [ ] Extractor registered in the dispatch table in `extractors.py`
- [ ] Fixture repo extended in `tests/test_cortex.py::make_fixture_repo` covering symbols, imports, calls, at least one route/decorator convention
- [ ] Redaction applied to any free-text field you emit
- [ ] `python -m unittest discover tests` green

## Adding an MCP tool

The server is intentionally tiny: `src/cortex/mcp_server.py` holds everything.

1. Implement the handler as `def tool_<name>(args: dict) -> list[dict]` returning `[{"type": "text", "text": ...}]`. Reuse existing query functions from `src/cortex/search.py` / `contextpack.py` / `session.py` — don't fork logic.
2. Register it in the `TOOLS` dict: `(description, json-schema-properties, handler, required-args)`. Write descriptions as agent-facing instructions ("call this when…"), not code comments.
3. Errors go in-band as text (`"error: ..."`); one bad frame must never kill the server.
4. Extend the round-trip self-test in `cli.py cmd_doctor` only if you add protocol surface.
5. Document it: add a row to the tool table in `README.md` and a section in `docs/MCP.md`.

## Project layout

```
bin/cortex                 CLI launcher script
src/cortex/
├── discovery.py           finds projects under configured roots (~/.cortex/config.json)
├── langs.py               file-type detection, ignored dirs, secret redaction
├── extractors.py          tree-sitter TS/TSX/JS/Go + ast py + regex SQL/prisma
├── indexer.py             full + incremental indexing, importance scoring
├── gitmine.py             history mining, categories, hotspots, co-change
├── search.py              hybrid retrieval: BM25 FTS5 + IDF overlap + graph + anchors
├── contextpack.py         budgeted context packets + impact analysis
├── session.py             task sessions, episodes, decay, quality metrics
├── ingest_reports.py      curated reports → memories/modules/flows/decisions
├── vault.py               Obsidian vault generator
├── db.py                  SQLite connect + migration runner
├── mcp_server.py          zero-dep MCP stdio server
├── migrations/*.sql       numbered schema migrations, auto-applied
└── cli.py                 command surface (cortex …)
tests/                     unittest suite (fixture repos built on the fly)
```

The public repository documents benchmark methodology in `docs/BENCHMARKS.md`. The
maintainer's raw ground truth references private repositories and is intentionally not
published; public regression coverage belongs in the throwaway fixtures under `tests/`.
