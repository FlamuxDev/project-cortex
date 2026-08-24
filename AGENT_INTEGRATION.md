# Agent Integration

## The 30-second rule for any coding agent

Drop this block into your project instructions (CLAUDE.md / AGENTS.md / system prompt):

```markdown
## Project Cortex
This machine indexes all repos under ~/Dev into Project Cortex.
Before non-trivial exploration:
1. `cortex context "<task>"` (or MCP tool cortex_context) — read the packet FIRST.
2. Read only the PRIMARY FILES it names; expand only if evidence is insufficient.
3. Before changing a symbol/file: `cortex impact "<path>"` — respect callers/tests listed.
4. Run RELATED TESTS from the packet before declaring done.
5. If a section says EVIDENCE WARNING, verify in-repo before trusting matches.
6. After durable architectural/business changes: `cortex update <project>`.
```

That's the whole integration. It saves tokens by design.

## MCP wiring

Server: `cortex serve` (stdio JSON-RPC, zero deps).

**Claude Code** (`~/.claude.json` or project `.mcp.json`):
```json
{ "mcpServers": { "cortex": { "command": "/home/aboud/.local/bin/cortex", "args": ["serve"] } } }
```

**OpenCode** (`~/.config/opencode/opencode.json`):
```json
{ "mcp": { "cortex": { "type": "local", "command": ["/home/aboud/.local/bin/cortex", "serve"] } } }
```

**Codex CLI** (`~/.codex/config.toml`):
```toml
[mcp_servers.cortex]
command = "/home/aboud/.local/bin/cortex"
args = ["serve"]
```

**Generic MCP client**: initialize → tools/list → tools/call. Protocol version 2024-11-05.

## Tool selection guide

| You need | Tool |
|---|---|
| Task briefing under a token budget | `cortex_context {task, project?, budget?}` |
| Cross-project ("have we done X elsewhere") | same tool — phrasing like "across projects" auto-triggers |
| Locate code lexically | `cortex_search {query, project?}` |
| Definition of a named symbol | `cortex_symbol {name, project?}` |
| Who calls/imports a file | `cortex_callers {path, symbol?, project?}` |
| Blast radius before editing | `cortex_impact {target, project?}` |
| Tests to run | `cortex_tests {target, project?}` |
| Module purpose/invariants/pitfalls | `cortex_module {name, project?}` |
| Is the brain current? | `cortex_status {project}` |
| Refresh after pulling/committing | `cortex_update {project?}` |
| Recent history for a path | `cortex_history {project, path?, category?}` |
| What changed since commit X | `cortex_changed_since {project, since}` |

## Rules of trust

- Deterministic layers (symbols, refs, routes, tables, commits) are facts from AST/git.
- Prose memories carry `[confidence]` tags; `[STALE]` means evidence paths changed since ingest.
- `EVIDENCE WARNING` sections mean: some task terms don't exist in that repo — don't force it.
- When HEAD ≠ indexed commit, packets say so. Run `cortex update` to refresh.
