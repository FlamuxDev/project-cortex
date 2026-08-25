---
cortex-generated: true
title: luma tests
tags: [tests/project]
---

# Luma — Test Map

146 test files.

| Kind | Count |
|---|---|
| integration | 34 |
| unit | 112 |

## integration (34)

- `ai-engine/tests/assert-db-integration-ran.test.js` — covers 1 targets
- `ai-engine/tests/incident-bundle-read-only.integration.test.js` — covers 4 targets
- `ai-engine/tests/integration/integration.test.js` — covers 4 targets
- `ai-engine/tests/provenance/cli.integration.test.js`
- `ai-engine/tests/provenance/worker-store-integration.test.js` — covers 10 targets
- `ai-engine/tests/triage-read-only.integration.test.js` — covers 3 targets
- `ai-engine/tests/worker-multi-process.integration.test.js` — covers 1 targets
- `ai-engine/tests/worker-postgres.integration.test.js` — covers 5 targets
- `ai-engine/tests/worker-provider-faults.integration.test.js` — covers 8 targets
- `ai-engine/tests/worker-regenerate-section.integration.test.js` — covers 6 targets
- `ai-engine/tests/worker-retry.integration.test.js` — covers 7 targets
- `backend-luma/tests/integration/admin.repository.test.js`
- `backend-luma/tests/integration/agent-messages.test.js`
- `backend-luma/tests/integration/agent-runs.test.js`
- `backend-luma/tests/integration/agent.repository.test.js`
- `backend-luma/tests/integration/agent.service.test.js`
- `backend-luma/tests/integration/auth.security.test.js`
- `backend-luma/tests/integration/auth.test.js`
- `backend-luma/tests/integration/blueprint-events.test.js`
- `backend-luma/tests/integration/blueprint-sections.test.js`
- `backend-luma/tests/integration/blueprints.test.js`
- `backend-luma/tests/integration/db.test.js`
- `backend-luma/tests/integration/diagram.test.js`
- `backend-luma/tests/integration/exportFile.test.js`
- `backend-luma/tests/integration/middlewares.test.js`
- `backend-luma/tests/integration/response-contracts.test.js`
- `backend-luma/tests/integration/security-logs.test.js`
- `backend-luma/tests/integration/setup.js`
- `backend-luma/tests/integration/superadmin.repository.test.js`
- `backend-luma/tests/integration/superadmin.service.test.js`
- `backend-luma/tests/integration/user.service.test.js`
- `backend-luma/tests/integration/worker-agent-runs.test.js`
- `backend-luma/tests/integration/worker-messages-sections-reviews.test.js`
- `backend-luma/tests/integration/worker-queue.test.js`

## unit (112)

- `ai-engine/quality/evaluator/evaluate.test.js` — covers 1 targets
- `ai-engine/scripts/benchmark/report/csv.test.js` — covers 1 targets
- `ai-engine/src/config/index.test.js` — covers 1 targets
- `ai-engine/src/data/backend-data-source.test.js` — covers 1 targets
- `ai-engine/src/data/http-client.test.js` — covers 2 targets
- `ai-engine/src/data/index.test.js` — covers 4 targets
- `ai-engine/src/data/prisma-data-source.test.js` — covers 1 targets
- `ai-engine/src/lib/logger.test.js` — covers 1 targets
- `ai-engine/src/orchestration/agents/registry.test.js` — covers 2 targets
- `ai-engine/src/orchestration/context/budgets.test.js` — covers 1 targets
- `ai-engine/src/orchestration/context/context-manager.test.js` — covers 4 targets
- `ai-engine/src/orchestration/context/interaction-matrix.test.js` — covers 3 targets
- `ai-engine/src/orchestration/context/summaries.test.js` — covers 1 targets
- `ai-engine/src/orchestration/debate/coordinator.test.js` — covers 2 targets
- `ai-engine/src/orchestration/debate/resolution.test.js` — covers 2 targets
- `ai-engine/src/orchestration/debate/section-history.test.js` — covers 3 targets
- `ai-engine/src/orchestration/debate/threads.test.js` — covers 1 targets
- `ai-engine/src/orchestration/events/publish.test.js` — covers 2 targets
- `ai-engine/src/orchestration/pipeline/criticality.test.js` — covers 1 targets
- `ai-engine/src/orchestration/pipeline/prompt-assembly.test.js` — covers 1 targets
- `ai-engine/src/orchestration/pipeline/resume.test.js` — covers 2 targets
- `ai-engine/src/orchestration/pipeline/run-agent.test.js` — covers 5 targets
- `ai-engine/src/orchestration/pipeline/run-state.test.js` — covers 2 targets
- `ai-engine/src/orchestration/pipeline/scheduler.test.js` — covers 1 targets
- `ai-engine/src/orchestration/pipeline/sectioner.test.js` — covers 2 targets
- `ai-engine/src/orchestration/pipeline/validator-dispatch.test.js` — covers 1 targets
- `ai-engine/src/orchestration/pipeline/workflow-builder.test.js` — covers 2 targets
- `ai-engine/src/orchestration/providers/ambiguous-write-guard.test.js` — covers 2 targets
- `ai-engine/src/orchestration/providers/gemini-adapter.test.js` — covers 1 targets
- `ai-engine/src/orchestration/providers/health.test.js` — covers 2 targets
- `ai-engine/src/orchestration/providers/log-leak.test.js`
- `ai-engine/src/orchestration/providers/mock-provider.test.js` — covers 3 targets
- `ai-engine/src/orchestration/providers/openai-adapter.test.js` — covers 1 targets
- `ai-engine/src/orchestration/providers/resilient-provider.test.js` — covers 2 targets
- `ai-engine/src/orchestration/providers/token-accountant.test.js` — covers 2 targets
- `ai-engine/src/orchestration/providers/with-retry.test.js` — covers 3 targets
- `ai-engine/src/orchestration/queue/claim.test.js` — covers 2 targets
- `ai-engine/src/orchestration/queue/lease.test.js` — covers 2 targets
- `ai-engine/src/orchestration/regenerate/audit.test.js` — covers 2 targets
- `ai-engine/src/orchestration/regenerate/handler.test.js` — covers 5 targets
- `ai-engine/src/orchestration/regenerate/payload.test.js` — covers 2 targets
- `ai-engine/src/orchestration/regenerate/policy.test.js` — covers 3 targets
- `ai-engine/src/orchestration/retry/audit.test.js` — covers 2 targets
- `ai-engine/src/orchestration/retry/handler.test.js` — covers 6 targets
- `ai-engine/src/orchestration/retry/payload.test.js` — covers 2 targets
- `ai-engine/src/orchestration/retry/policy.test.js` — covers 3 targets
- `ai-engine/src/orchestration/triage/bundle.test.js` — covers 3 targets
- `ai-engine/src/orchestration/triage/classifier.test.js` — covers 2 targets
- `ai-engine/src/orchestration/triage/evidence.test.js` — covers 4 targets
- `ai-engine/src/orchestration/triage/export.test.js` — covers 3 targets
- …and 62 more

## High-importance code with no obvious mapped test

_Heuristic (name/import match). Verify before treating as gaps._

- `backend-luma/src/routes/worker.routes.js`
- `backend-luma/src/loaders/routes.loader.js`
- `backend-luma/src/routes/superadmin.routes.js`
- `backend-luma/src/routes/auth.routes.js`
- `backend-luma/src/routes/blueprint.routes.js`
- `backend-luma/src/routes/agentRun.routes.js`
- `backend-luma/src/routes/diagram.routes.js`
- `backend-luma/src/routes/exportFile.routes.js`
- `LUMA_FontEnd/src/api/api.js`
- `backend-luma/src/routes/admin.routes.js`
- `backend-luma/src/routes/agentMessage.routes.js`
- `backend-luma/src/routes/agent.routes.js`
- `backend-luma/src/routes/user.routes.js`
- `ai-engine/src/orchestration/pipeline/section-map.js`
- `backend-luma/src/routes/section.routes.js`
- `ai-engine/src/lib/placeholder-role.js`
- `ai-engine/scripts/benchmark/invariants/utils.js`
- `ai-engine/src/orchestration/model.js`
- `backend-luma/src/app.js`
- `backend-luma/src/loaders/express.loader.js`
- `backend-luma/src/middlewares/rateLimiterMiddlewares.js`
- `backend-luma/src/routes/blueprintEvent.route.js`
- `ai-engine/scripts/benchmark/runner/run-scenario.js`
- `ai-engine/src/provenance/git.js`
- `ai-engine/scripts/benchmark/report/statistics.js`
