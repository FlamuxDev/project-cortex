# Task Sessions

Every non-trivial task gets a tracked session — the spine of the learning loop.

## Lifecycle

```bash
cd /home/aboud/Dev/my-project        # cwd auto-detection engages
cortex task start "fix booking validation"
#   → SESSION #N, freshness check, full context packet (files/symbols/tests/past lessons)
#     suggested files/symbols/tests are stored for later precision scoring
cortex impact "src/bookings/service.ts"    # auto-logged to the open session
# ... implement, test ...
cortex task complete --session N --outcome tested \
  --problem "duplicate bookings on retry" \
  --root-cause "retry re-entered create without idempotency key" \
  --lessons "Never retry BookingService.create without a request fingerprint." \
  --tests-run "apps/api/test/booking.spec.ts"
```

Agents do the same via MCP tools `cortex_task_start` / `cortex_task_complete`.

## What is stored (and what never is)

Stored per session: project, task text (redacted), start HEAD, freshness state,
context size, suggested files/symbols/tests, impact queries, files touched
(attributed via git diff), outcome, end HEAD, computed metrics.

**Never stored:** chain-of-thought, model transcripts, secrets (everything passes
`langs.redact()` before persistence), env values.

## Attribution rules

- Files already dirty **before** `task start` are excluded from session evidence
  unless the session's committed range includes them.
- Only changes between start-HEAD and completion are attributed; concurrent
  external commits show up as `commits_in_range` in metrics.
- `--outcome tested|verified` with zero file changes is rejected outright.

## Outcomes

`implemented` → `tested` → `verified` (strong→stronger evidence) · `partial`
(discovery-only work) · `failed` (lesson kept, tagged FAILED ATTEMPT in packets)
· `abandoned` (closed without episode unless lessons provided).

## Inspection

```bash
cortex task list            # last 20 sessions
cortex task show <id>       # full session + episode detail
cortex quality              # aggregate hit rates + health
```
