# Episodes

An episode is the durable engineering memory of one completed task: what changed,
why, the root cause, invariants discovered, failed approaches, and the evidence
behind every claim.

## Fields

| Field | Source |
|---|---|
| task, project | session at `task start` |
| problem, root_cause, solution, lessons, failed_approaches | agent-provided (redacted) or deterministic fallback summary |
| files_modified, symbols, modules, apis, db_entities, mapped_tests | **gathered automatically** from git diff + index at completion |
| commit_sha / parent_sha | explicit or derived from clean working tree |
| confidence | `verified` (commit + lessons) / `strongly_inferred` / `inferred` |
| status | `active` → `uncertain`/`obsolete` (evidence decayed) / `superseded` |
| metrics_json | precision/recall of that session's Cortex suggestions |

## Automatic generation

`cortex task complete` (or MCP `cortex_task_complete`) gathers deterministic
evidence — no manual episode writing. The extraction model contract: agents pass
validated `lessons`; Cortex never invents claims. Lessons containing invariant
markers ("never", "always", "must"…) are auto-promoted to memories with full
provenance (`derived_from: episode:N @ sha`).

## Retrieval

Episodes enter future packets only when relevant (`PAST TASK LESSONS` section):
same project + keyword/symbol/API/module overlap with the new task. Failed
attempts surface tagged `[failed ATTEMPT — do not repeat]`. A booking lesson does
not leak into a CSS task. Junk lessons fail the relevance gate and stay dormant.

## Promotion

```bash
cortex episode promote 12 --scope global   # explicit human decision only
```
Auto-promotion caps at module/pitfall scope within the episode's own project.
Dedup runs per-project+scope and ignores project-name tokens, so a mushagil
lesson can never be suppressed by a telvora lookalike.

## Decay & contradiction

On every `cortex update` / `cortex doctor`: episodes whose evidence files vanished
→ `obsolete`; whose symbols all disappeared → `uncertain`; generated memories
inherit the flag. **Reversible**: if evidence returns, state flips back to
`active`. Contradiction candidates (old vs newer episode sharing ≥2 files) are
reported for human review — never auto-deleted.

```bash
cortex episode list
cortex episode supersede <id> [--by <newer-id>] [--status uncertain]
```

## What makes a good lesson

Good: *"Retrying booking creation after an upstream timeout can duplicate bookings
because the DB commit may already have succeeded; always carry the idempotency key."*
Bad: *"Fixed booking bug successfully."*
