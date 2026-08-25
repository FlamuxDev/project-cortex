---
cortex-generated: true
title: luma code map
tags: [codemap/project]
---

# Luma — Code Map

## Directory layout (indexed files)

- `ai-engine/` — 274 files
- `backend-luma/` — 176 files
- `LUMA_FontEnd/` — 25 files
- `dev-all.js/` — 1 files
- `luma_backup.sql/` — 1 files

## Entry points

- `ai-engine/src/data/index.js`
- `ai-engine/src/config/index.js`
- `ai-engine/src/worker/index.js`
- `ai-engine/scripts/benchmark/report/index.js`
- `ai-engine/scripts/benchmark/invariants/index.js`
- `backend-luma/src/config/index.js`
- `backend-luma/src/models/index.js`
- `backend-luma/src/server.js`

## Most-connected symbols (fan-in leaders)

| Symbol | Kind | Location |
|---|---|---|
| `create` | function | `backend-luma/src/repositories/refreshToken.repository.js:5` |
| `create` | function | `backend-luma/src/repositories/role.repository.js:19` |
| `createPrismaDataSource` | function | `ai-engine/src/data/prisma-data-source.js:59` |
| `withRetry` | function | `ai-engine/src/orchestration/providers/with-retry.js:32` |
| `get` | function | `backend-luma/tests/integration/worker-messages-sections-reviews.test.js:176` |
| `createFakeDataSource` | function | `ai-engine/src/data/test-double.js:110` |
| `buildManifest` | function | `ai-engine/src/provenance/manifest.js:61` |
| `parseConfig` | function | `ai-engine/src/config/index.js:273` |
| `createFilesystemProvenanceStore` | function | `ai-engine/src/provenance/lifecycle/filesystem-provenance-store.js:52` |
| `main` | function | `ai-engine/src/worker/index.js:298` |
| `main` | function | `ai-engine/prisma/seed-drill.mjs:42` |
| `main` | function | `ai-engine/scripts/run-staging-smoke.mjs:65` |
| `main` | function | `ai-engine/scripts/verify-restore-invariants.mjs:57` |
| `runAgentWithRetry` | function | `ai-engine/src/orchestration/pipeline/run-agent.js:66` |
| `classifyFailure` | function | `ai-engine/src/orchestration/triage/classifier.js:63` |
| `handleRetryJob` | function | `ai-engine/src/orchestration/retry/handler.js:115` |
| `section` | function | `ai-engine/src/orchestration/regenerate/policy.test.js:51` |
| `section` | function | `ai-engine/src/orchestration/triage/markdown.js:25` |
| `recordRetryAudit` | function | `ai-engine/src/orchestration/retry/audit.js:30` |
| `checkCrossSectionConsistency` | function | `ai-engine/src/orchestration/validation/consistency.js:213` |
| `processGenerateJob` | function | `ai-engine/src/worker/generate-job.js:201` |
| `record` | function | `ai-engine/src/data/backend-data-source.test.js:12` |
| `generateJob` | function | `ai-engine/src/orchestration/triage/export.test.js:86` |
| `redact` | function | `ai-engine/src/orchestration/triage/redaction.js:66` |
| `hashText` | function | `ai-engine/src/provenance/fingerprint.js:20` |
| `createEvidenceRecord` | function | `ai-engine/src/provenance/lifecycle/evidence-record.js:51` |
| `runProvenanceStoreCli` | function | `ai-engine/src/provenance/store-cli.js:236` |
| `createWorkerMetrics` | function | `ai-engine/src/worker/metrics.js:42` |
| `generateJob` | function | `ai-engine/tests/incident-bundle-cli.test.js:38` |
| `generateJob` | function | `ai-engine/tests/triage-job.test.js:115` |

## Highest-importance files

- `backend-luma/src/routes/worker.routes.js` (123 loc)
- `backend-luma/src/loaders/routes.loader.js` (67 loc)
- `ai-engine/src/data/index.js` (68 loc)
- `backend-luma/src/routes/superadmin.routes.js` (280 loc)
- `ai-engine/src/data/test-double.js` (186 loc)
- `ai-engine/src/config/index.js` (283 loc)
- `backend-luma/src/routes/auth.routes.js` (279 loc)
- `backend-luma/src/routes/blueprint.routes.js` (174 loc)
- `backend-luma/src/routes/agentRun.routes.js` (174 loc)
- `LUMA_FontEnd/src/i18n.jsx` (1990 loc)
- `ai-engine/src/worker/generate-job.js` (672 loc)
- `ai-engine/src/lib/prisma.js` (65 loc)
- `backend-luma/src/routes/diagram.routes.js` (221 loc)
- `backend-luma/src/routes/exportFile.routes.js` (169 loc)
- `LUMA_FontEnd/src/page/newblueprint2.jsx` (3858 loc)
- `LUMA_FontEnd/src/api/api.js` (162 loc)
- `ai-engine/src/orchestration/providers/errors.js` (28 loc)
- `ai-engine/src/lib/logger.js` (31 loc)
- `backend-luma/src/routes/admin.routes.js` (112 loc)
- `backend-luma/src/routes/agentMessage.routes.js` (148 loc)
- `ai-engine/src/orchestration/providers/token-accountant.js` (293 loc)
- `ai-engine/src/orchestration/validation/core.js` (221 loc)
- `ai-engine/src/worker/index.js` (784 loc)
- `ai-engine/src/orchestration/pipeline/prompt-assembly.js` (112 loc)
- `ai-engine/src/orchestration/retry/errors.js` (35 loc)