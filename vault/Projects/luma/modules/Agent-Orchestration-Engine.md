---
cortex-generated: true
title: agent-orchestration-engine
tags: [module]
---

# Agent orchestration engine

**Project:** [[luma]] | **Confidence:** inferred | **verified@** `da7bced5651b`
**Owns:** `ai-engine/src/`

purpose: background worker that claims generation jobs, materializes one AgentRun per council agent, executes them in dependency batches through LLM providers, validates output, persists sections/diagrams/messages, and settles jobs truthfully.
path_prefixes: ai-engine/src/
key_files: src/worker/index.js, src/worker/generate-job.js, src/orchestration/pipeline/workflow-builder.js, src/orchestration/pipeline/scheduler.js, src/orchestration/pipeline/run-agent.js, src/orchestration/providers/resilient-provider.js, src/orchestration/validation/core.js, prisma/seed.js
entrypoints: npm run worker[:dev|:once]; playground/injection/regression scripts in scripts/
responsibilities: lease renewal + stale recovery, heartbeat, metrics, drain/shutdown signals, token accounting, retry policies, provenance CLI (`scripts/provenance-cli.mjs`).
invariants: state machines are closed — Job `queued→running→completed|failed|cancelled`; unsupported job types must fail, never pass through (`UnsupportedJobTypeError`, index.js:27); final settlement is compare-and-set so late cancellations can't be overwritten.
pitfalls: exits at startup when backend unreachable (by design); validator set (brooks/diffie/grove/norman/torvalds…) is mid-refactor on the dirty tree.
confidence: high

## Files (40+)

- `ai-engine/src/config/index.js`
- `ai-engine/src/config/index.test.js`
- `ai-engine/src/data/backend-data-source.js`
- `ai-engine/src/data/backend-data-source.test.js`
- `ai-engine/src/data/errors.js`
- `ai-engine/src/data/http-client.js`
- `ai-engine/src/data/http-client.test.js`
- `ai-engine/src/data/index.js`
- `ai-engine/src/data/index.test.js`
- `ai-engine/src/data/port.js`
- `ai-engine/src/data/prisma-data-source.js`
- `ai-engine/src/data/prisma-data-source.test.js`
- `ai-engine/src/data/test-double.js`
- `ai-engine/src/lib/logger.js`
- `ai-engine/src/lib/logger.test.js`
- `ai-engine/src/lib/placeholder-role.js`
- `ai-engine/src/lib/prisma.js`
- `ai-engine/src/lib/worker-id.js`
- `ai-engine/src/orchestration/agents/registry.js`
- `ai-engine/src/orchestration/agents/registry.test.js`
- `ai-engine/src/orchestration/context/budgets.js`
- `ai-engine/src/orchestration/context/budgets.test.js`
- `ai-engine/src/orchestration/context/context-manager.js`
- `ai-engine/src/orchestration/context/context-manager.test.js`
- `ai-engine/src/orchestration/context/interaction-matrix.js`

## API surface

- `GET knuth`
- `GET brooks`
- `GET /api/agent-runs`
- `PATCH /api/agent-runs/1`
- `POST /api/agent-messages`
- `GET /api/blueprints/missing`
- `PATCH /api/blueprints/1`
- `GET /api/agent-runs/1`
- `GET turing`
- `GET hopper`
