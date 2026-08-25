# Project Cortex

**A local-first engineering brain for AI coding agents. Index your codebase once, retrieve narrow context forever — stop paying agents to re-explore the same repo on every task.**

[![CI](https://github.com/OWNER/cortex/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/cortex/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

Cortex is an MCP server + CLI that gives any coding agent (Claude Code, Codex CLI, OpenCode, Cursor, or any MCP client) precise task context in seconds: which module owns a feature, which files and symbols matter, who calls them, which tests must run, what past tasks taught you, and what may break — all inside an explicit token budget. It doubles as an **AI agent memory**: completed tasks become episodes whose lessons resurface exactly when relevant.

## The problem

- **Agents re-explore.** Every session re-greps the same tree, re-reads the same files, re-derives the same architecture map.
- **Tokens burn.** Discovery-by-grep costs hundreds of KB of context before real work starts.
- **Blast radius is invisible.** Agents edit shared symbols without knowing callers, served routes, or mapped tests.
- **Lessons evaporate.** The root cause your agent found last month is gone; the next agent repeats the mistake.

## Quickstart (30 seconds)

```bash
pipx install git+https://github.com/OWNER/cortex.git
cortex init ~/code/myapp          # register + index one repo (or a dir of repos)
cortex context "fix booking validation"
```

Real packet output (abridged) — sections are priority-ordered and fit your budget:

```
## HEADER
PROJECT: myapp (myapp)
PATH: /home/me/code/myapp
STACK: ts,tsx | frameworks: next,drizzle
FRESHNESS: fresh

## MODULE
bookings [verified]
purpose: reservation lifecycle — create/confirm/cancel/refund
owns: apps/api/src/business/bookings/

## PRIMARY FILES
apps/api/src/business/bookings/service.ts
apps/api/src/business/bookings/controller.ts

## PRIMARY SYMBOLS
apps/api/src/business/bookings/service.ts:31 class BookingService  export class BookingService {

## TESTS TO RUN
src/__tests__/bookings.test.ts (unit DIRECT)

## PAST TASK LESSONS
validated knowledge from previous tasks in this project:
- [tested | verified] fix duplicate bookings on retry
  Always carry the idempotency key when retrying BookingService.create.
```

If task terms don't exist in the repo, the packet says so up front:

```
## ⚠ EVIDENCE WARNING
These task terms appear NOWHERE in this project's indexed paths/symbols: refunds.
The feature may not exist here or uses other terminology. Matches below share only
partial terms (validation) — verify before acting.
```

## What your agents get

Run `cortex serve` and point your MCP client at it. 16 tools:

| Tool | What it does |
|---|---|
| `cortex_task_start` | Tracked session: auto-detects project from cwd, freshness check, full briefing packet |
| `cortex_task_complete` | Closes the session, gathers git evidence, records a durable episode with lessons |
| `cortex_quality` | Learning-loop health: hit rates, episode counts, decay flags |
| `cortex_context` | Budgeted context packet for a task (no tracking) |
| `cortex_search` | Hybrid lexical+graph search across code, symbols, knowledge |
| `cortex_impact` | Blast radius before editing: dependents, tests, APIs, DB entities, risk |
| `cortex_module` | Module memory: purpose, owned files, invariants, pitfalls |
| `cortex_symbol` | Definition lookup by exact name |
| `cortex_references` | Files referencing/calling a named symbol |
| `cortex_callers` | Callers + importers of a file (optionally one symbol) |
| `cortex_tests` | Tests covering a file/target |
| `cortex_projects` | All indexed projects |
| `cortex_status` | Per-project index status/freshness |
| `cortex_update` | Incremental re-index after pulling/committing |
| `cortex_history` | Recent commits, filtered by path/category |
| `cortex_changed_since` | Files changed since a given commit |

Full reference with call/response sketches: [`docs/MCP.md`](docs/MCP.md)

## The learning loop

```
            ┌──────────────────────────────────────────────────────┐
            │                                                      │
            ▼                                                      │
      ┌──────────┐   ┌────────┐   ┌────────────┐   ┌───────────┐   │
      │  task    │──▶│context │──▶│  impact    │──▶│ implement │   │
      │ arrives  │   │ packet │   │ (blast     │   │           │   │
      └──────────┘   └────────┘   │  radius)   │   └─────┬─────┘   │
                                  └────────────┘         ▼         │
      ┌──────────────┐   ┌──────────┐   ┌────────────────────┐     │
      │ next task    │◀──│ episode  │◀──│ test               │     │
      │ starts       │   │ (lessons,│   └────────────────────┘     │
      │ smarter      │   │ evidence,│                              │
      └──────────────┘   │ root     │         cortex task complete │
                         │ cause)   │◀─────────────────────────────┘
                         └──────────┘
```

Every completed task becomes an episode. Relevant lessons surface in future packets (`PAST TASK LESSONS`); failed attempts surface tagged "do not repeat". Evidence decay is checked on every update — lessons whose code vanished are flagged, never silently trusted.

## Why it works without embeddings, daemons, or cloud

- **Deterministic indexing.** tree-sitter (TS/TSX/JS/Go) + stdlib `ast` (Python) + regex extractors (SQL/Prisma) → SQLite + FTS5. Same input, same index, no model drift.
- **Hybrid retrieval beats vectors here.** BM25 + IDF keyword overlap + import/call graph + memory anchors hit 20/20 on the retrieval eval *without* an embedding pipeline. No service to run, nothing to phone home.
- **Local-only.** One SQLite file under `~/.cortex`. No accounts, no sync, no telemetry.
- **Secrets stay out.** Every signature/doc/commit subject passes redaction before insert; `.pem` dirs are excluded at discovery; env var *names* may be stored, values never.

## Benchmarks

Honest labels — measured on real repos, or simulated policies over real tools:

| Benchmark | Result | Type |
|---|---|---|
| Retrieval eval (20 realistic questions, 14 projects, budget 3000) | **20/20 pass**, p50 latency 0.02s | Measured |
| Arabic / mixed-language retrieval eval | **8/8 pass** | Measured |
| Token cost to locate correct code area vs unaided grep-and-read policy | **~94% median reduction** (~174–187 KB → ~10–12 KB per task) | Simulated baseline policy over real repos |

Details: [`RETRIEVAL_EVALUATION.md`](RETRIEVAL_EVALUATION.md) · [`TOKEN_EFFICIENCY_BENCHMARK.md`](TOKEN_EFFICIENCY_BENCHMARK.md) · [`ARABIC_EVALUATION.json`](ARABIC_EVALUATION.json). Eval questions were authored by the builder (optimism bias acknowledged in the doc); scripts are rerunnable.

## How it compares

| | Raw grep/exploration | CLAUDE.md-style rules only | LSP servers | Cortex |
|---|---|---|---|---|
| Setup | none | hand-written per repo | per-language servers | `cortex init <dir>` once |
| Finds right file/symbol for a task | slow, token-hungry | only what you pre-wrote | precise but low-level (needs a query plan) | budgeted packet in one call |
| Cross-file blast radius | no | no | yes (IDE-grade) | yes (retrieval-grade: callers, tests, APIs, DB) |
| Remembers past tasks | no | no | no | episodes + lessons resurface by relevance |
| Git intelligence (hotspots, past fixes) | no | no | no | yes |
| Runtime | none | none | heavy, language-specific | one Python process, zero daemons |

Positioning is deliberate: Cortex is **retrieval-grade, not IDE-grade**. It finds what matters fast; LSPs rename better. They compose — Cortex tells your agent where and what to verify.

## Agent setup

**Claude Code**
```bash
claude mcp add --scope user cortex -- cortex serve
```

**Codex CLI** (`~/.codex/config.toml`)
```toml
[mcp_servers.cortex]
command = "cortex"
args = ["serve"]
```

**OpenCode** (`~/.config/opencode/opencode.json`)
```json
{ "mcp": { "cortex": { "type": "local", "command": ["cortex", "serve"] } } }
```

**Generic MCP client:** JSON-RPC over stdio, protocol `2024-11-05`, zero dependencies. Spawn `cortex serve`, then `initialize` → `tools/list` → `tools/call`.

Then drop this into your `AGENTS.md` / `CLAUDE.md`:

```markdown
Before non-trivial exploration: call cortex_task_start (or `cortex context "<task>"`) and read the packet first.
Read only the PRIMARY FILES it names. Before changing a symbol: cortex_impact. Run RELATED TESTS before done.
```

## Architecture

Deterministic extraction → SQLite brain (FTS5) → hybrid ranking → budgeted packets. Freshness is recomputed live from git at every query; stored state is never trusted. See [`docs/ARCHITECTURE_PUBLIC.md`](docs/ARCHITECTURE_PUBLIC.md).

## Contributing

PRs welcome — conventional commits, `python -m unittest discover tests` must pass. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

MIT — see [`LICENSE`](LICENSE).
