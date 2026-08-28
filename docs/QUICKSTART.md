# Quickstart: zero to first context packet in 5 minutes

## 1. Install

Requires Python 3.11+ and `git` on PATH.

```bash
# isolated command install (recommended)
pipx install git+https://github.com/FlamuxDev/project-cortex.git

# uv works too
uv tool install git+https://github.com/FlamuxDev/project-cortex.git

# editable source checkout, if you plan to hack on it
git clone https://github.com/FlamuxDev/project-cortex.git
cd project-cortex
pip install -e .
```

The only runtime dependencies are `tree-sitter` and its language grammars (TypeScript, JavaScript, Python, Go) — installed automatically.

Verify:

```bash
cortex status        # "0 projects indexed" is fine at this point
```

## 2. Register repos with `cortex init`

**Single repo** — the root may itself be a git repo or any project dir:

```bash
cortex init ~/code/myapp
```

**Directory of repos** — every indexable project under the dir is registered (needs ≥3 code files each):

```bash
cortex init ~/code
```

`init` saves the root to `~/.cortex/config.json`, runs a full index, and prints agent wiring commands. Re-running `init` with a new path adds another root; nothing is deleted.

Index speed: roughly a minute for a mid-sized repo; large monorepos take longer. Incremental updates afterwards run in seconds.

## 3. Get your first packet

Run inside any indexed repo (project auto-detected from cwd):

```bash
cd ~/code/myapp
cortex context "fix booking validation"
```

Or name a project explicitly / query across all projects:

```bash
cortex context "where do we validate webhooks?" --project myapp
cortex context "have we implemented tenant isolation across projects?" --all
```

Budget control — sections are priority-ordered (header/module/files/symbols → callers/tests → history/lessons), never randomly truncated:

```bash
cortex context "<task>" --budget small   # 2000 tokens: header + module + primary files
cortex context "<task>" --budget 6000    # deep: adds symbols/callers/history/episodes
```

## 4. Wire your agents

```bash
# Claude Code
claude mcp add --scope user cortex -- cortex serve

# Codex CLI: ~/.codex/config.toml
[mcp_servers.cortex]
command = "cortex"
args = ["serve"]

# OpenCode: ~/.config/opencode/opencode.json
{ "mcp": { "cortex": { "type": "local", "command": ["cortex", "serve"] } } }
```

Generic MCP clients: spawn `cortex serve` (JSON-RPC over stdio), then `initialize` → `tools/list` → `tools/call`. See [`docs/MCP.md`](MCP.md).

MCP servers can outlive one editor workspace. Pass the `project` id (or optional `cwd`)
on context/task calls when the client does not launch a separate server per repository.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `CORTEX_HOME` | `~/.cortex` | State dir holding `config.json`, `glossary.json` and `data/` |
| `CORTEX_ROOTS` | *(unset)* | Colon-separated override for configured roots, e.g. `/work/repos:/oss`. Takes precedence over `config.json` |
| `CORTEX_DATA_DIR` | `$CORTEX_HOME/data/cortex.db` | Path to the SQLite brain |
| `CORTEX_FTS_SYMBOL_CAP` | `100000` | Symbols per project entering full-text search, by importance |
| `CORTEX_FTS_FILE_CAP` | `20000` | Files per project entering full-text search |

Example: keep everything out of `$HOME`:

```bash
export CORTEX_HOME=/data/cortex-home
export CORTEX_DATA_DIR=/data/cortex-home/brain.db
```

Upgrading from a pre-0.3 checkout: the brain used to live at `<checkout>/data/cortex.db`.
That file is still picked up automatically if it exists, so nothing breaks — move it to
`~/.cortex/data/cortex.db` when convenient (stop `cortex serve` first, and take the
`-wal`/`-shm` siblings with it).

## Non-English tasks

Cortex bridges non-English task wording to English identifiers via a term glossary, so
`"عدل booking validation"` retrieves the same code as the English phrasing. The shipped
Arabic table (`cortex/data/glossary_ar.json`) is a generic starter — extend it for your own
domain by creating `$CORTEX_HOME/glossary.json`:

```json
{
  "terms": {
    "شحنة": ["shipment", "delivery"],
    "مرتجع": ["refund", "return"]
  }
}
```

User entries are merged over the shipped ones (same key wins), so you can both add new
terms and override the defaults. A missing or malformed file is ignored rather than
breaking search.

## Daily loop

```bash
cortex update                 # incremental re-index after pulling/committing
cortex impact "src/auth.ts"   # blast radius before risky edits
cortex doctor                 # health checks incl. live MCP round-trip + redaction self-test
```

## Running the tests

```bash
python -m unittest discover tests     # stdlib unittest suite, no fixtures needed
```

(Tests build tiny throwaway fixture repos internally; they don't touch your real index.)

## Troubleshooting

**tree-sitter wheel install fails** (older Pythons, musl/alpine): you need a compiler toolchain (`gcc`/`clang`) so the grammar wheels can build from source, or use a Python version with prebuilt wheels (3.11–3.13 on glibc Linux/macOS). Check with `python -c "import tree_sitter"`.

**"no indexable projects found under <dir>"**: discovery needs ≥3 code files per project and skips generated/ignored dirs. If the target itself is one repo, `cortex init <repo-dir>` directly instead of the parent.

**Non-git repos work fine.** Git mining (history, hotspots, freshness-vs-HEAD) is skipped gracefully; everything else operates normally.

**Project not detected when running commands:** pass `--project <id>` explicitly, or run inside the repo — cwd detection wins otherwise.

**Packet says the brain is behind by N commits:** someone committed since indexing. Run `cortex update <project>` (or `cortex update` for all roots).

**Packet says `DIRTY`:** uncommitted code may differ from the last index. Run `cortex update <project>` or verify the cited files directly before editing.
