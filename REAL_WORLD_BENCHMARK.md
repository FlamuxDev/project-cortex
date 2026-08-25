# Real-World Benchmark

_Generated 2026-08-25 from `task_sessions` — MEASURED data only._

## Method

Every real task run through `cortex task start` / `cortex task complete` records:
context packet size at start, files Cortex suggested, files actually touched
(git diff attributed to the session), and precision/recall of suggestions.
Baseline (no-cortex discovery cost) is NOT fabricated: until we log unaided sessions side-by-side, only the Cortex column exists. The simulated ~94% reduction in TOKEN_EFFICIENCY_BENCHMARK.md remains clearly labeled simulated.

## Aggregate (measured)

| Metric | Value |
|---|---|
| Tasks measured | 10 |
| Median context packet | 7,999 chars (~1,999 tokens) |
| Primary-file hit rate | None |
| Suggestion recall | None |
| Test-recommendation hit rate | None |
| Episodes captured | 9 active / 9 total |

## Per-task log

| # | project | outcome | suggested | touched | precision | recall | context tok~ |
|---|---|---|---|---|---|---|---|
| #1 | mushagil | partial | - | - | - | - | 2,995 |
| #2 | cvm | partial | - | - | - | - | 2,881 |
| #3 | luma | partial | - | - | - | - | 1,050 |
| #4 | telvora | partial | - | - | - | - | 1,709 |
| #5 | mawid-ai | partial | - | - | - | - | 2,110 |
| #6 | sham-v2 | partial | - | - | - | - | 133 |
| #7 | mushagil | abandoned | - | - | - | - | 1,330 |
| #8 | mushagil | partial | 10 | 0 | 0.0 | None | 2,599 |
| #9 | mushagil | abandoned | 10 | 0 | 0.0 | None | 1,999 |
| #10 | mushagil | partial | 10 | 0 | 0.0 | None | 1,999 |
