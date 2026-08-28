# Benchmarks

All numbers below were produced by rerunnable scripts against **real private repositories**
(a mix of TypeScript monorepos, Next.js apps, Go services and Python backends, 6k+ files,
67k+ symbols indexed). Repository names are anonymized as *Repo A–F*; everything else —
methodology, task shape, raw counts — is reported as measured.

Honest labels are used throughout: **Measured** means the tool was run and the output
recorded; **Simulated** means a policy was modelled over real tools and real ground truth.

| Benchmark | Result | Type |
|---|---|---|
| Retrieval eval — 18 questions, 13 projects, budget 3000 | **18/18 pass**, p50 0.03s | Measured |
| Arabic / mixed-language retrieval eval — 7 questions | **7/7 pass** | Measured |
| Token cost to locate the right code area vs. unaided grep-and-read | **~94% median reduction** | Simulated policy, real repos |

---

## 1. Retrieval evaluation

**Maintainer runner:** `scripts/retrieval_eval.py` (private ground-truth bundle; methodology below)

### Setup

18 realistic engineering questions across 13 projects (knowledge-base ingestion, tenant
isolation leaks, voice LLM 404s, webhook signature verification, Arabic tasks, frontend
bugs…). Each has curated ground truth — a file/symbol substring verified to exist in the
repo. PASS = the ground truth appears in the budget-3000 context packet.

### Result

```
Score: 18/18 (100%)        latency p50 = 0.03s, max = 0.30s
tokens per packet: 650–3000 (budget 3000)
```

The suite was 20 questions across 14 projects when authored. One evaluated repository was
later deleted and purged from the brain, so its 2 questions were removed with it — the
count dropped to 18, not the pass rate. While that project was deleted-but-still-indexed,
the suite scored 19/20: Cortex kept serving its stale rows and reporting them as fresh.
That failure mode is tracked in [`LIMITATIONS.md`](LIMITATIONS.md).

### How it got there (the self-improvement loop)

| Iteration | Change | Score | Notable failure fixed |
|---|---|---|---|
| 1 | plain BM25, AND-semantics | — | multi-term queries returned nothing on paths |
| 2 | OR-recall BM25 | 18/20 | noisy single-term matches outranked real targets |
| 3 | + keyword-overlap rerank | 19/20 | a Go webhook handler stayed buried under FTS scale |
| 4 | + IDF guarantee sweep | 19/20 | BM25 magnitude still dominated |
| 5 | normalized signals + memory anchors + live freshness | **20/20** | — |

An independent adversarial audit then found cross-project, nonexistent-feature and
freshness weaknesses. Fixes landed for all three — cross-project round-robin retrieval,
the `EVIDENCE WARNING` guardrail, and live git freshness — and the eval still passed 20/20
at that point.

### Known limits of this eval

**The questions were authored by the builder, with knowledge of the indexed repos.
Optimism bias is real and is not corrected for here.** The adversarial and hallucination
audits exist precisely to counter it, but they do not make this an independent benchmark.
Treat the score as evidence the retrieval path works on realistic questions — not as a
competitive score against other tools.

---

## 2. Token efficiency

**Maintainer runner:** `scripts/token_benchmark.py` (private) · **Type: simulated policy over real repos**

### Methodology

Two agent policies are simulated over the same repositories with identical ground truth
per task:

- **Baseline (no cortex)** — how an unaided agent explores: extract task keywords, run
  `rg -li` per keyword over the repo, then open candidate files (first 150 lines each)
  until a file matching the curated ground truth appears. Cost = every byte surfaced
  (rg output + opened file heads).
- **Cortex** — one `cortex context` packet at budget 3000 tokens, plus reading the
  top-listed primary file's first 150 lines. Cost = packet bytes + that read.

Cost metric = **bytes the agent must consume to locate the correct implementation area.**
This isolates *discovery* cost. It is not a claim about end-to-end task success.

### Results

| Repo | Task | Baseline | Cortex | Reduction |
|---|---|---|---|---|
| Repo A | duplicate knowledge-base ingestion | ~171 KB (not found) | ~9 KB ✓ | 95% |
| Repo B | tenant isolation leak | ~242 KB ✓ | ~11 KB ✓ | 95% |
| Repo C | analytics route registration | ~188 KB (not found) | ~9 KB ✓ | 95% |
| Repo D | webhook signature verification | ~184 KB (not found) | ~12 KB ✓ | 94% |
| Repo E | voice LLM bridge 404 | ~369 KB (not found) | ~7 KB ✓ | 98% |
| Repo F | WhatsApp webhook dedupe | ~138 KB (not found) | ~6 KB ✓ | 96% |

**Median: baseline ≈ 174–187 KB vs cortex ≈ 10–12 KB → ~94–95% reduction.**

"(not found)" means the baseline policy exhausted 30 file reads without confirming the
target — so its cost is a floor, not a completion.

### Observations

- The baseline frequently failed to *confirm* the target even when `rg` surfaced it —
  filename-only matches don't prove relevance without reading.
- Cortex packets land in the 1.5k–2.6k token range at budget 3000, fitting typical
  "startup context" allowances with room to spare.
- The dominant cortex cost is the packet itself. Primary-file reads are usually
  unnecessary for *locating* work and are counted here as conservative overhead.

### Known limits

The baseline is a **modelled policy, not a recorded agent session.** A human or a smarter
agent would grep more cleverly and might find the target sooner. The comparison is
directional evidence about discovery cost, not a controlled head-to-head.

---

## 3. Arabic / mixed-language retrieval

**Maintainer runner:** `scripts/arabic_eval.py` (private ground-truth bundle)

Arabic and code-switched Arabic/English tasks against English codebases — the realistic
case for an Arabic-speaking developer. PASS uses the same ground-truth rule as §1.

| # | Task | Repo | Pass | Tokens |
|---|---|---|---|---|
| 1 | وين نظام الحجوزات؟ | Repo F | ✓ | 2640 |
| 2 | وين الشي الي يمنع duplicate requests؟ | Repo G | ✓ | 1136 |
| 4 | صلح validation حق campaign | Repo B | ✓ | 1928 |
| 5 | وين tenant isolation؟ | Repo C | ✓ | 2221 |
| 6 | غير ال authentication flow تبع login | Repo E | ✓ | 1342 |
| 7 | وين ال worker الي يسوي embedding؟ | Repo D | ✓ | 2212 |
| 8 | عدل webhook handler حق whatsapp | Repo H | ✓ | 2070 |

**Score: 7/7.** (An eighth question targeted a repository later deleted, and was removed with it.)

This works through an Arabic→English term bridge plus Arabic-aware tokenization
(U+061F and friends stripped, definite-article `ال` handling, naive plural bridging).

### Known limits

**The glossary was written against these repos' vocabulary**, so this score partly measures
glossary coverage rather than retrieval quality in general. The glossary ships as
`cortex/data/glossary_ar.json` and is extended per install via `$CORTEX_HOME/glossary.json`
— see [`QUICKSTART.md`](QUICKSTART.md). Arabic tasks in an uncovered domain will need
entries added before they retrieve as well as these do.

---

## Reproducing

The eval scripts read from your own indexed brain and need ground truth curated for your
repos, so they are not runnable as-is against a fresh install. The methodology above is
complete enough to reimplement; the runners live alongside the maintainer's private
evaluation set.

The **honest summary**: these benchmarks were built and run by the author against the
author's own repositories. They demonstrate the system works on real code at real scale.
They are not third-party validation, and are not presented as such.
