# Token Efficiency Benchmark

**Date:** 2026-08-25 · **Script:** `scripts/token_benchmark.py` · rerunnable.

## Methodology (honest)

Simulated agent policies over real tools, identical ground truth per task:

- **Baseline (no cortex):** the way an unaided agent explores — extract task keywords,
  run `rg -li` per keyword over the repo, then open candidate files (first 150 lines each)
  until a file matching the curated ground truth appears. Cost = every byte surfaced
  (rg output + opened file heads).
- **Cortex:** one `cortex context` packet at budget 3000 tokens, plus reading the top-listed
  primary file's first 150 lines. Cost = packet bytes + that read.

Cost metric = bytes the agent must consume to locate the correct implementation area.
(Not a claim about end-to-end task success; it isolates *discovery* cost.)

## Results

| Project | Task | Baseline | Cortex | Reduction |
|---|---|---|---|---|
| mushagil | duplicate knowledge-base ingestion | ~171 KB (not found) | ~9 KB ✓ | 95% |
| campify | tenant isolation leak | ~242 KB ✓ | ~11 KB ✓ | 95% |
| cvm | analytics route registration | ~188 KB (not found) | ~9 KB ✓ | 95% |
| telvora | webhook signature verification | ~184 KB (not found) | ~12 KB ✓ | 94% |
| chat-agent-saas | voice LLM bridge 404 | ~369 KB (not found) | ~7 KB ✓ | 98% |
| mawid-ai | WhatsApp webhook dedupe | ~138 KB (not found) | ~6 KB ✓ | 96% |

**Median: baseline ≈ 174–187 KB vs cortex ≈ 10–12 KB → ~94–95% reduction.**

## Observations

- Baseline policy frequently failed to *confirm* the target within 30 file reads even when
  `rg` surfaced it — filename-only matches don't prove relevance without reading.
- Cortex packets land in the 1.5k–2.6k token range at budget 3000 — they fit typical
  "startup context" allowances with room to spare.
- The dominant cortex cost is the packet itself; primary-file reads are usually unnecessary
  for *locating* work and are included here as a conservative overhead.

## Reproduce

```bash
cd ~/project-cortex && .venv/bin/python scripts/token_benchmark.py
```
