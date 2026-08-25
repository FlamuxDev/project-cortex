# CORTEX_WORKFLOW — the mandatory loop

> **Cortex first. Broad repository exploration only when Cortex evidence is insufficient.**

## The loop (what every agent does now)

```
task arrives
 → cortex_task_start / cortex task start     (auto project detection + freshness + packet)
 → verify critical claims in cited source    (packet marks confidence; EVIDENCE WARNING = go look)
 → cortex impact <target>                    (before cross-module/API/schema/shared-symbol edits)
 → implement
 → run suggested tests
 → cortex task complete                      (evidence gathered automatically, lessons recorded)
 → next agent starts smarter                 (PAST TASK LESSONS section)
```

## Where it's enforced

1. **Agent instruction files** — all 14 projects under `~/Dev` carry the compact
   Cortex policy block (`<!-- project-cortex:v1 -->` marker) in CLAUDE.md/AGENTS.md.
2. **MCP auto-discovery** — `cortex serve` registered for Claude Code (~/.claude.json),
   OpenCode (~/.config/opencode/opencode.json), Codex (~/.codex/config.toml).
3. **Friction asymmetry** — one `cortex_task_start` call replaces six manual calls;
   skipping it means blind exploration.

## Budgets

```bash
cortex context "<task>" --budget 2000   # small: header/module/primary files only
cortex context "<task>" --budget 6000   # deep: adds symbols/callers/history/episodes
cortex context "<task>" --budget small|normal|deep   # named modes
```

Sections are priority-ordered and never randomly truncated: architecture facts →
primary files/symbols → callers/invariants → tests → past lessons → history.

## Trust rules

- Deterministic layers (symbols/routes/tables/git) are facts.
- Prose knowledge carries `[confidence]`; `[STALE]`/`uncertain` flags mean verify first.
- `EVIDENCE WARNING` = some task terms don't exist in this repo — don't force a match.
- Project guessed from wording alone says so in the packet; zero-evidence guesses are refused.

## Health

```bash
cortex doctor    # MCP round-trip, migrations, redaction self-test, decay, graph integrity
cortex quality   # measured hit rates (n≥3), episode health, stale memory count
```
