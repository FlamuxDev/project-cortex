---
cortex-generated: true
title: evaluation-benchmarks
tags: [module]
---

# evaluation & benchmarks

**Project:** [[luma]] | **Confidence:** inferred | **verified@** `da7bced5651b`
**Owns:** `ai-engine/quality/,ai-engine/tests/,ai-engine/scripts/`

purpose: mutation-suite evaluator, injection corpus (prompt-injection resistance), regression runner with runtime budget, capacity smoke/matrix benchmarks.
path_prefixes: ai-engine/quality/, ai-engine/tests/, ai-engine/scripts/
key_files: quality/evaluator/evaluate.js, scripts/run-injection-corpus.js, scripts/run-regression.js, scripts/benchmark/runner/run-smoke.js
entrypoints: npm run quality:pilot | regression | injection | capacity:smoke | capacity:full
confidence: medium

## Files (40+)

- `ai-engine/quality/evaluator/evaluate.js`
- `ai-engine/quality/evaluator/evaluate.test.js`
- `ai-engine/scripts/agent-playground.js`
- `ai-engine/scripts/assert-db-integration-ran.mjs`
- `ai-engine/scripts/benchmark/invariants/duplicate-logical-runs.js`
- `ai-engine/scripts/benchmark/invariants/duplicate-terminal-events.js`
- `ai-engine/scripts/benchmark/invariants/false-completed-jobs.js`
- `ai-engine/scripts/benchmark/invariants/index.js`
- `ai-engine/scripts/benchmark/invariants/utils.js`
- `ai-engine/scripts/benchmark/profiles/smoke.js`
- `ai-engine/scripts/benchmark/report/csv.js`
- `ai-engine/scripts/benchmark/report/csv.test.js`
- `ai-engine/scripts/benchmark/report/index.js`
- `ai-engine/scripts/benchmark/report/markdown.js`
- `ai-engine/scripts/benchmark/report/statistics.js`
- `ai-engine/scripts/benchmark/report/summary.js`
- `ai-engine/scripts/benchmark/runner/collect-results.js`
- `ai-engine/scripts/benchmark/runner/create-workload.js`
- `ai-engine/scripts/benchmark/runner/run-matrix.js`
- `ai-engine/scripts/benchmark/runner/run-scenario.js`
- `ai-engine/scripts/benchmark/runner/run-smoke.js`
- `ai-engine/scripts/benchmark/runner/worker-processes.js`
- `ai-engine/scripts/generate-worker-schema-contract.mjs`
- `ai-engine/scripts/provenance-cli.mjs`
- `ai-engine/scripts/provenance-store-cli.mjs`

## API surface

- `GET knuth`
