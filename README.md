# Project Cortex

A permanent, local-first **engineering brain** for every project under `~/Dev`.

> Index deeply once, retrieve narrowly forever.

Cortex gives any coding agent (or you) precise task context in seconds: which module owns a feature,
which files/symbols matter, who calls them, which tests must run, what business rules apply, what
past commits teach, and what may break — inside an explicit token budget.

## Quick start

```bash
cortex status                          # overall / per-project state
cortex projects                        # list everything indexed
cortex context "Fix duplicate knowledge-base document ingestion"
cortex context "Where have we implemented tenant isolation across projects?" --all
cortex impact "apps/api/src/business/knowledge.controller.ts" --project mushagil
cortex search "webhook signature" --project telvora
cortex module knowledge --project mushagil
cortex tests "src/auth.ts" --project fixture
cortex update                          # incremental re-index of every repo
cortex doctor                          # health checks
```

Arabic works too:

```bash
cortex context "عدل جزئية قاعدة المعرفة"
```

## MCP server (for coding agents)

```bash
cortex serve    # JSON-RPC/MCP over stdio, zero dependencies
```

13 tools: `cortex_context`, `cortex_search`, `cortex_impact`, `cortex_module`, `cortex_symbol`,
`cortex_references`, `cortex_callers`, `cortex_tests`, `cortex_projects`, `cortex_status`,
`cortex_update`, `cortex_history`, `cortex_changed_since`.
See `AGENT_INTEGRATION.md` for Ox / Claude Code / OpenCode / Codex wiring.

## What lives here

```
project-cortex/
├── bin/cortex            CLI launcher
├── src/cortex/           the engine (Python 3.13+, stdlib + tree-sitter)
│   ├── discovery.py      finds projects under ~/Dev
│   ├── extractors.py     tree-sitter TS/TSX/JS/Go + ast py + regex SQL/prisma
│   ├── indexer.py        full + incremental indexing, importance scoring
│   ├── gitmine.py        history mining, hotspots, co-change
│   ├── ingest_reports.py delegate report → memories/modules/flows/decisions
│   ├── search.py         hybrid retrieval (BM25 FTS5 + graph + IDF + memory anchors)
│   ├── contextpack.py    budgeted context packets + impact analysis
│   ├── mcp_server.py     zero-dep MCP stdio server
│   ├── vault.py          Obsidian vault generator
│   └── cli.py
├── data/cortex.db        SQLite brain (FTS5)
├── vault/                Obsidian-compatible knowledge vault (~200 notes)
├── projects/<id>/REPORT.md   deep-analysis reports (delegate-produced)
├── scripts/              evals, benchmarks, seeding
├── tests/                unittest suite
└── migrations applied automatically on first connect
```

## Rebuild from scratch

```bash
cd ~/project-cortex
uv venv .venv && uv pip install --python .venv/bin/python \
    tree-sitter tree-sitter-typescript tree-sitter-python tree-sitter-go tree-sitter-javascript
rm -f data/cortex.db*
.venv/bin/python src/cortex/indexer.py        # cold index (~14 min; mythos dominates)
.venv/bin/python src/cortex/ingest_reports.py # semantic layer from reports
.venv/bin/python scripts/seed_global_knowledge.py
.venv/bin/python src/cortex/vault.py          # regenerate Obsidian vault
ln -sf ~/project-cortex/bin/cortex ~/.local/bin/cortex
```

## Daily usage

- Start any task with `cortex context "<task>"` (or let your agent call the MCP tool).
- Before changing a symbol: `cortex impact "<file>"`.
- After pulling/committing: `cortex update` (incremental, seconds).
- Browse `vault/Home.md` in Obsidian for the human view.
