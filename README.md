# Project Cortex

**Local-first codebase intelligence and durable engineering memory for AI coding agents.**

[![CI](https://github.com/FlamuxDev/project-cortex/actions/workflows/ci.yml/badge.svg)](https://github.com/FlamuxDev/project-cortex/actions/workflows/ci.yml)
[![GitHub release](https://img.shields.io/github/v/release/FlamuxDev/project-cortex)](https://github.com/FlamuxDev/project-cortex/releases)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Project Cortex indexes a repository once, then gives Codex, Claude Code, Cursor,
OpenCode, and any MCP client a narrow evidence packet for each engineering task:
the owning module, primary files and symbols, callers, tests, blast radius, git
history, and lessons from earlier work.

It runs locally. There is no account, cloud service, telemetry, embedding API, or
background daemon.

### Why it stands out

- **Live Context Guard:** every task/context call fingerprints the exact indexable
  working tree and incrementally refreshes it only when code changed. Uncommitted
  edits are indexed but still labeled `DIRTY`; concurrent agent processes share a
  per-project refresh lock.
- **Architecture in one call:** `cortex_architecture` maps scale, languages, areas,
  boundaries, entrypoints, dependency hotspots, APIs, data entities, and test shape.
- **Git-aware preflight:** `cortex_preflight` reviews the whole current diff—not just
  one guessed symbol—and returns risk, affected callers, public/data surfaces, and
  the tests most likely to matter.
- **Memory with evidence:** completed work becomes a durable episode linked to files,
  commits, tests, and confidence; stale evidence is surfaced rather than silently
  trusted.
- **Portable agent workflow:** one bundled Agent Skill works across Codex, Claude
  Code, Cursor, OpenCode, and other Agent Skills-compatible clients; MCP exposes the
  same evidence as structured tools.

## Why Cortex

Coding agents are capable, but they repeatedly pay the same discovery cost:

- re-reading the repository before every task;
- spending context on broad grep results instead of the relevant code;
- changing shared code without seeing callers, routes, schemas, or mapped tests;
- losing root-cause knowledge when a session ends;
- trusting stale notes after the source has changed.

Cortex turns repository structure and verified task outcomes into a reusable,
freshness-aware evidence layer.

```text
task ──> context packet ──> impact check ──> implementation ──> tests
  ^                                                               │
  └──────── relevant lessons <── durable episode <── task complete ┘
```

## Install and get a first result

Requirements: Python 3.11+ and `git` on `PATH`.

```bash
# Install the isolated CLI from GitHub
pipx install git+https://github.com/FlamuxDev/project-cortex.git

# Register and index one repository, or point at a directory of repositories
cortex init ~/code/myapp

# Install the bundled Agent Skill for your local coding agents
cortex agents install

# Ask Cortex for a task packet
cd ~/code/myapp
cortex context "fix booking validation"

# Understand an unfamiliar repo, then review your current changes
cortex architecture
cortex preflight
```

`uv` works as well:

```bash
uv tool install git+https://github.com/FlamuxDev/project-cortex.git
```

To develop Cortex itself:

```bash
git clone https://github.com/FlamuxDev/project-cortex.git
cd project-cortex
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
python -m unittest discover tests
```

Verify the installation with:

```bash
cortex --version
cortex doctor
```

## Agent Skill: one command, automatic discovery

Cortex ships a portable [Agent Skills](https://agentskills.io) workflow at
[`project-cortex/SKILL.md`](.agents/skills/project-cortex/SKILL.md). The skill
teaches an agent when to start a tracked task, how to use narrow symbol and
reference lookup, when to check impact, which tests to run, and how to preserve
only verified lessons.

Install it globally:

```bash
cortex agents install
```

The installer writes the same bundled skill to the standard user discovery
locations without overwriting local modifications:

| Agents | Discovery path |
|---|---|
| Codex, Cursor, OpenCode | `~/.agents/skills/project-cortex/` |
| Claude Code | `~/.claude/skills/project-cortex/` |

After that, supported agents advertise the skill automatically and select it
when a task matches its description. You can also invoke it explicitly as
`$project-cortex` in Codex or `/project-cortex` in clients that use slash skills.

For a team-shared, repository-scoped installation, run this from the target
repository and commit the generated skill directories:

```bash
cortex agents install --scope project
```

Re-running the command is idempotent. If an installed copy was customized,
Cortex reports a conflict and preserves it. Use `--force` only when you intend
to restore the version shipped with Cortex.

The skill can drive the CLI by itself. For the best experience—native structured
tool calls instead of shell commands—connect the MCP server too.

## Connect the MCP server

Cortex uses JSON-RPC over stdio. Every client starts its own `cortex serve`
process; there is no port or long-running daemon to manage.

### Codex

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.cortex]
command = "cortex"
args = ["serve"]
```

### Claude Code

```bash
claude mcp add --transport stdio --scope user cortex -- cortex serve
```

### Cursor

Add to `~/.cursor/mcp.json` for global use, or `.cursor/mcp.json` in one project:

```json
{
  "mcpServers": {
    "cortex": {
      "type": "stdio",
      "command": "cortex",
      "args": ["serve"]
    }
  }
}
```

### OpenCode

Add to `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "cortex": {
      "type": "local",
      "command": ["cortex", "serve"],
      "enabled": true
    }
  }
}
```

### Any MCP client

Configure a local stdio server with command `cortex` and argument `serve`.
Cortex implements MCP protocol `2024-11-05`; the lifecycle is
`initialize` → `tools/list` → `tools/call`.

For long-lived MCP processes, pass `project` or the optional `cwd` on task and
context calls. A server process cannot observe an editor changing workspaces.

## What the agent receives

```text
SESSION #42 | project=myapp | freshness=fresh | index=refreshed

## MODULE
bookings [verified]
purpose: reservation lifecycle — create/confirm/cancel/refund

## PRIMARY FILES
apps/api/src/business/bookings/service.ts
apps/api/src/business/bookings/controller.ts

## PRIMARY SYMBOLS
apps/api/src/business/bookings/service.ts:31 class BookingService

## RELATED TESTS
src/__tests__/bookings.test.ts (unit DIRECT)

## PAST TASK LESSONS
- [tested | verified] Always carry the idempotency key when retrying create.
```

Sections are priority-ordered and constrained by an explicit token budget. If
important task terms do not appear in indexed paths, symbols, or content, Cortex
emits an evidence warning instead of presenting a weak match as certainty.

## Recommended agent workflow

With MCP:

1. `cortex_task_start` — resolve the project, auto-refresh changed code, and return
   a tracked context packet.
2. On an unfamiliar repository or architecture task, call `cortex_architecture`;
   otherwise read the packet's primary files and use `cortex_symbol`,
   `cortex_references`, or `cortex_callers` for narrow follow-up.
3. Call `cortex_impact` before cross-module, API, schema, or shared-symbol edits.
4. Implement, then call `cortex_preflight` to review the complete Git diff and run
   its related tests.
5. Call `cortex_update`, then `cortex_task_complete` with the real outcome, tests,
   and durable lessons.

CLI-only equivalent:

```bash
cortex task start "fix booking validation"
cortex architecture                # useful on an unfamiliar repository
cortex impact "BookingService"
# edit and test
cortex preflight --base HEAD        # or --base origin/main for the whole branch
cortex update myapp
cortex task complete --session 42 --outcome tested \
  --tests-run "pytest tests/test_booking.py" \
  --lessons "Retries must preserve the booking idempotency key."
```

Completed tasks become episodes. Cortex resurfaces relevant lessons on later
tasks and marks knowledge uncertain or obsolete when its source evidence
changes.

## MCP tools

Cortex exposes 18 focused tools:

| Tool | Purpose |
|---|---|
| `cortex_task_start` | Start a tracked task and return the full briefing packet |
| `cortex_task_complete` | Close the session and store evidence-backed lessons |
| `cortex_context` | Get a budgeted packet without task tracking |
| `cortex_search` | Search code, symbols, and memory with hybrid ranking |
| `cortex_impact` | Estimate blast radius across callers, tests, APIs, and DB entities |
| `cortex_architecture` | Map repository structure, boundaries, hotspots, and surfaces |
| `cortex_preflight` | Map a Git diff to risk, dependents, APIs/data, and tests |
| `cortex_module` | Read module purpose, owned paths, invariants, and pitfalls |
| `cortex_symbol` | Find an exact symbol definition |
| `cortex_references` | Find files that reference or call a symbol |
| `cortex_callers` | Find callers and importers of a file or symbol |
| `cortex_tests` | Find tests mapped to a target |
| `cortex_projects` | List indexed projects and live state |
| `cortex_status` | Inspect freshness and index counts |
| `cortex_update` | Incrementally re-index changed files and decay stale memory |
| `cortex_history` | Query relevant commit history |
| `cortex_changed_since` | List indexed files changed since a commit |
| `cortex_quality` | Measure learning-loop coverage and health |

See the complete argument and response reference in [`docs/MCP.md`](docs/MCP.md).

## CLI reference

| Command | Purpose |
|---|---|
| `cortex init <path>` | Register and fully index one repo or a directory of repos |
| `cortex agents install` | Install the bundled global Agent Skill |
| `cortex agents install --scope project` | Install team-shareable project skills |
| `cortex context "<task>"` | Print a task context packet |
| `cortex search "<query>"` | Search indexed files, symbols, and memories |
| `cortex impact "<target>"` | Inspect likely blast radius before editing |
| `cortex architecture` | Print the repository's structural map and hotspots |
| `cortex preflight [--base origin/main]` | Review current/branch changes and tests before merge |
| `cortex tests "<target>"` | Show mapped tests |
| `cortex update [project]` | Incrementally refresh the index |
| `cortex task start/complete` | Use the tracked learning loop from the shell |
| `cortex quality` | Inspect memory and retrieval quality |
| `cortex doctor` | Run storage, graph, redaction, migration, and MCP checks |
| `cortex serve` | Start the stdio MCP server |

Run `cortex <command> --help` for all options.

## How it works

```text
repositories
   │
   ├─ deterministic parsers: tree-sitter + Python ast + SQL/Prisma extractors
   ├─ git history, hotspots, freshness, and changed-file evidence
   └─ tests, routes, imports, calls, modules, and database entities
                         │
                         ▼
             local SQLite + FTS5 + graph edges
                         │
                         ▼
            hybrid ranking + token-budgeted packets
                         │
                         ▼
                   CLI or MCP agents
```

- TypeScript, TSX, JavaScript, Python, Go, SQL, and Prisma are indexed.
- BM25, identifier overlap, graph proximity, and memory anchors drive retrieval.
- SQLite WAL mode supports multiple agent clients safely.
- The Live Context Guard content-fingerprints indexable changes before task/context,
  refreshes incrementally, and serializes concurrent refreshes per project.
- Versioned index markers trigger a safe one-time derived-data repair when indexing
  logic changes; a clean repository does not need a cold re-parse after upgrading.

This is retrieval-grade code intelligence, not an IDE-grade refactoring engine.
Cortex finds what matters and what may break; an LSP remains better for exact
renames and type-aware edits.

## Privacy and storage

All state stays under `~/.cortex` by default:

| Variable | Default | Purpose |
|---|---|---|
| `CORTEX_HOME` | `~/.cortex` | Configuration, glossary, and data directory |
| `CORTEX_ROOTS` | unset | Colon-separated override for indexed roots |
| `CORTEX_DATA_DIR` | `$CORTEX_HOME/data/cortex.db` | SQLite database path |
| `CORTEX_FTS_SYMBOL_CAP` | `100000` | Per-project symbol FTS cap |
| `CORTEX_FTS_FILE_CAP` | `20000` | Per-project file FTS cap |

Cortex does not send repository data anywhere. Signatures, documentation, and
commit subjects pass through secret redaction before storage; private-key paths
and common generated directories are excluded during discovery. Environment
variable names may be indexed, but values are not.

## Benchmarks

| Evaluation | Result | Label |
|---|---:|---|
| Retrieval, 18 realistic questions across 13 projects at budget 3000 | **18/18 pass**, p50 0.03 s | Measured |
| Arabic and mixed-language retrieval, 7 questions | **7/7 pass** | Measured |
| Context used to locate the right code area vs a grep-and-read policy | **~94% median reduction** | Simulated baseline over real repos |

The questions were authored by the builder against the builder's own repos, so
optimism bias is possible. Methodology, raw scope, and limitations are documented
in [`docs/BENCHMARKS.md`](docs/BENCHMARKS.md).

## Updating and troubleshooting

Upgrade the application and refresh its bundled skill:

```bash
pipx upgrade project-cortex
cortex agents install
cortex update
```

If the installed skill was changed or came from an older release, review the
conflict and use `cortex agents install --force` to replace only Cortex's shipped
files. Extra files in the skill directory are preserved.

Common checks:

- `cortex status --project <id>` — verify the selected project and freshness.
- `cortex projects` — list valid project ids and roots.
- `cortex update <id>` — refresh a packet that reports behind or dirty state.
- `cortex doctor` — validate migrations, FTS, graph health, redaction, and a live
  MCP round-trip.

Non-git repositories are supported; only git history and commit-distance
freshness are unavailable. Discovery requires at least three indexable code
files per project and intentionally skips common generated directories.

More help: [`docs/QUICKSTART.md`](docs/QUICKSTART.md) and
[`docs/LIMITATIONS.md`](docs/LIMITATIONS.md).

## Documentation

- [Quickstart](docs/QUICKSTART.md)
- [MCP reference](docs/MCP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Benchmarks](docs/BENCHMARKS.md)
- [Known limitations](docs/LIMITATIONS.md)
- [Security policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)

## Contributing

Issues and pull requests are welcome. Use conventional commits and run:

```bash
python -m unittest discover tests
ruff check --select F src tests
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the development workflow.

## License

MIT — see [`LICENSE`](LICENSE).
