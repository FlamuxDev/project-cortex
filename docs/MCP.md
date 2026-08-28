# MCP Reference

Cortex ships a zero-dependency MCP server speaking JSON-RPC 2.0 over stdio (protocol `2024-11-05`).

```bash
cortex serve
```

## Lifecycle

- **stdio transport, one process per client session.** Your MCP client spawns `cortex serve` and talks newline-delimited JSON-RPC on stdin/stdout. No daemon, no ports.
- The server opens its SQLite connection at startup; concurrent clients each get their own process — SQLite WAL mode handles this safely.
- Project resolution: explicit `project` wins, then optional `cwd`, then an explicit project name in the task, then the server process's working directory. Long-lived servers should receive `project` or `cwd`; the server cannot observe an editor's later directory changes. Ambiguity returns an error rather than guessing from generic task vocabulary.
- Handshake: `initialize` → `notifications/initialized` → `tools/list` / `tools/call`.

## Tools (16)

### cortex_task_start

Starts a tracked task session, checks freshness against live git, returns a full context packet, and stores suggested files/symbols/tests for later precision scoring.

| Arg | Type | Required | Notes |
|---|---|---|---|
| `task` | string | ✓ | natural-language task |
| `project` | string | | overrides cwd detection |
| `cwd` | string | | absolute client workspace path when `project` is omitted |
| `budget` | number | | default 3000 |

Call this FIRST for any non-trivial task. When done, call `cortex_task_complete` with the returned session id.

```
→ tools/call {"name":"cortex_task_start","arguments":{"task":"fix booking validation"}}
← SESSION #42 | project=myapp | freshness=FRESH | ~2140 tokens

## HEADER
PROJECT: myapp (myapp) ...
## PRIMARY FILES
apps/api/src/business/bookings/service.ts ...
[hint] when done, call cortex_task_complete with session 42 and durable lessons.
```

### cortex_task_complete

Closes a task session: gathers deterministic evidence from the git diff + index (files modified, symbols, modules, APIs, DB entities, mapped tests), computes retrieval precision metrics for that session's suggestions, and stores an episode.

| Arg | Type | Required |
|---|---|---|
| `session_id` | number | ✓ |
| `outcome` | string (`implemented\|tested\|verified\|failed\|partial\|abandoned`) | |
| `problem` | string | |
| `root_cause` | string | |
| `lessons` | string | invariant knowledge worth remembering |
| `failed_approaches` | string | what not to repeat |
| `tests_run` | array of strings | |
| `commit_sha` | string | |

```
→ tools/call {"name":"cortex_task_complete","arguments":{"session_id":42,
    "outcome":"tested","root_cause":"retry re-entered create without idempotency key",
    "lessons":"Never retry BookingService.create without a request fingerprint.",
    "tests_run":["src/__tests__/bookings.test.ts"]}}
← { "session_id": 42, "episode_id": 17, "confidence": "verified", ... }
  files_modified: apps/api/src/business/bookings/service.ts
```

### cortex_quality

Learning-loop health: sessions started/completed, episode counts by state, hit rates (primary-file, suggestion recall, test-recommendation), stale memory count, decay flags. No args.

### cortex_context

Budgeted context packet without session tracking. Same packet as `cortex_task_start`, minus tracking.

| Arg | Type | Required | Notes |
|---|---|---|---|
| `task` | string | ✓ | |
| `project` | string | | |
| `cwd` | string | | absolute client workspace path when `project` is omitted |
| `budget` | number | | default 4000 |

Cross-project phrasing ("across projects", "elsewhere", "have we …") auto-switches to cross-project round-robin results grouped by project.

```
→ tools/call {"name":"cortex_context","arguments":{"task":"webhook signature verification","budget":3000}}
← ## HEADER ... ## PRIMARY FILES ... ## RELATED TESTS ... (~1.5–2.6k tokens)
```

### cortex_search

Hybrid lexical+graph search across symbols, memories, and files in one call.

| Arg | Type | Required |
|---|---|---|
| `query` | string | ✓ |
| `project` | string | |

```
→ tools/call {"name":"cortex_search","arguments":{"query":"webhook signature"}}
← myapp src/workers/webhooks.ts:88 [function] verifySignature
  GLOBAL [business_rule/verified] Webhook payloads are verified with HMAC-SHA256 ...
  myapp src/workers/webhooks.ts
```

### cortex_impact

Blast radius before changing a file/symbol/feature: direct dependents (callers+importers+barrel fallback), BFS indirect dependents, mapped tests, served API routes, touched DB entities, risk level with reasons, past fixes on those exact files. Auto-logged to any open task session.

| Arg | Type | Required |
|---|---|---|
| `target` | string | ✓ file path or symbol/feature name |
| `project` | string | |
| `session` | number | attach result to this session |

```
→ tools/call {"name":"cortex_impact","arguments":{"target":"src/bookings/service.ts"}}
← { "risk": "high",
    "reasons": ["12 dependent files", "serves 3 API route(s)"],
    "direct_dependents": ["apps/api/src/routes/bookings.ts", "..."],
    "tests": ["src/__tests__/bookings.test.ts"],
    "apis": ["POST /bookings", "DELETE /bookings/:id"],
    "past_fixes": ["a1b2c3 2026-08-14 [fix] prevent duplicate booking on retry"] }
```

### cortex_module

Module memory: purpose, owned path prefixes, invariants, pitfalls, indexed file count.

| Arg | Type | Required |
|---|---|---|
| `name` | string | ✓ slug/name substring match |
| `project` | string | |

```
→ tools/call {"name":"cortex_module","arguments":{"name":"bookings"}}
← # bookings [verified] verified@a1b2c3d4e5f6
  purpose: reservation lifecycle — create/confirm/cancel/refund ...
  owns: apps/api/src/business/bookings/
```

### cortex_symbol

Definition lookup by exact name across all projects (or one), ordered by importance.

| Arg | Type | Required |
|---|---|---|
| `name` | string | ✓ exact symbol name |
| `project` | string | |

```
→ tools/call {"name":"cortex_symbol","arguments":{"name":"BookingService"}}
← myapp apps/api/src/business/bookings/service.ts:31-204 [class] export class BookingService {
```

### cortex_references

Files referencing/calling a named symbol (resolved call/use edges).

| Arg | Type | Required |
|---|---|---|
| `name` | string | ✓ |
| `project` | string | |

### cortex_callers

Callers and importers of a file, optionally scoped to one symbol within it.

| Arg | Type | Required |
|---|---|---|
| `path` | string | ✓ |
| `symbol` | string | |
| `project` | string | |

```
→ tools/call {"name":"cortex_callers","arguments":{"path":"src/auth.ts"}}
← calls into src/auth.ts:
    src/middleware/session.ts
  imports it:
    src/__tests__/auth.test.ts
```

### cortex_tests

Tests mapped to a target file (unit/integration/e2e, DIRECT flag = test directly imports it).

| Arg | Type | Required |
|---|---|---|
| `target` | string | ✓ |
| `project` | string | |

### cortex_projects

List all indexed projects: id, kind, live git/worktree freshness, languages. No args.

### cortex_status

Per-project live git/worktree freshness, code root, counts (files/symbols/modules/flows/apis/tests/stale memories), and last-index time.

| Arg | Type | Required |
|---|---|---|
| `project` | string | omitted → fleet summary |

### cortex_update

Incrementally re-index changed files (content-hash diff), mark intersecting memories stale, append new commits, run evidence decay. Omit `project` to update every root.

| Arg | Type | Required |
|---|---|---|
| `project` | string | |

### cortex_history

Recent mined commits, optionally filtered by file path and category (`fix`/`feat`/`refactor`/`docs`/`chore`).

| Arg | Type | Required |
|---|---|---|
| `project` | string | resolved via detection if omitted |
| `path` | string | filter to commits touching this path |
| `category` | string | |
| `limit` | number | default 12 |

### cortex_changed_since

Files changed in the repo since a given commit sha (per the brain's mined history).

| Arg | Type | Required |
|---|---|---|
| `project` | string | ✓ |
| `since` | string | ✓ commit sha (12-char prefix ok) |

## Trust rules for agents

- Deterministic layers (symbols, refs, routes, tables, commits) are facts from AST/git.
- Prose memories carry `[scope/confidence]`; `[STALE]` means their evidence paths changed since ingest — verify first.
- An `⚠ EVIDENCE WARNING` section means some task terms don't exist in that repo. Don't force a match.
- If HEAD ≠ indexed commit, packets say so and recommend `cortex_update`.
