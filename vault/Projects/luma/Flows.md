---
cortex-generated: true
title: luma flows
tags: [flows/project]
---

# Luma — Product Flows

End-to-end behaviors as verified from source. Files are the evidence trail.

## Blueprint generation (end-to-end)
**Trigger:** user submits idea on /new-blueprint (frontend) → POST /api/blueprints creates Blueprint (+BlueprintSettings) and a `generation_jobs` row (job_type=generate, status=queued).
*[[luma]] · confidence: high*

trigger: user submits idea on /new-blueprint (frontend) → POST /api/blueprints creates Blueprint (+BlueprintSettings) and a `generation_jobs` row (job_type=generate, status=queued).
steps: (1) worker claims oldest queued job atomically — `FOR UPDATE SKIP LOCKED` + fenced update (prisma mode) or claim endpoint (backend mode) — stamps `(workerId, leaseGeneration)`; (2) loads Blueprint + mandatory settings (DB values authoritative over payload copies); (3) workflow-builder loads active AgentDefinitions, applies security/devops skips, builds topological batches; (4) materializes one real AgentRun per agent (pending resumes, completed reused, non-stale duplicates fail closed); (5) per batch, context manager picks approved upstream output within budgets; provider adapter calls OpenAI/Gemini/mock; (6) output passes agent validators + canary leak filter + Mermaid gate (LUMA-212); (7) sectioner appends section revisions + diagrams atomically with their event message; (8) Knuth compiles final document; job settled via compare-and-set; (9) blueprint → completed; SSE pushes progress to viewer.
files: ai-engine/src/worker/generate-job.js, src/orchestration/pipeline/{scheduler,sectioner,workflow-builder}.js, src/orchestration/events/publish.js, backend-luma/src/controllers/worker.controller.js, LUMA_FontEnd/src/page/new-blueprint.jsx
confidence: high

**Files:**
- `ai-engine/src/worker/generate-job.js`
- `src/orchestration/pipeline/{scheduler`
- `sectioner`
- `workflow-builder}.js`
- `src/orchestration/events/publish.js`
- `backend-luma/src/controllers/worker.controller.js`
- `LUMA_FontEnd/src/page/new-blueprint.jsx`

## Live progress streaming (SSE)
**Trigger:** frontend opens EventSource on GET /api/blueprints/:id/events after starting generation.
*[[luma]] · confidence: high*

trigger: frontend opens EventSource on GET /api/blueprints/:id/events after starting generation.
steps: backend subscribes to blueprint events (pg_notify in prisma mode / written event rows otherwise) and streams to authenticated client; viewer renders sections/diagrams incrementally.
files: backend-luma/src/services/blueprintEvent.service.js, src/routes/blueprintEvent.route.js, LUMA_FontEnd/src/page/new-blueprint.jsx
confidence: high

**Files:**
- `backend-luma/src/services/blueprintEvent.service.js`
- `src/routes/blueprintEvent.route.js`
- `LUMA_FontEnd/src/page/new-blueprint.jsx`

## Stale-job recovery
**Trigger:** worker heartbeat/lease expiry or explicit recover endpoint.
*[[luma]] · confidence: high*

trigger: worker heartbeat/lease expiry or explicit recover endpoint.
steps: stale leased job requeued inside the same serializable transaction that flips its running AgentRuns back to pending and increments retry_count; resume restricted to the stuck job's own runs via generation_job_id (LUMA-172).
files: ai-engine/src/orchestration/pipeline/resume.js, src/orchestration/queue/lease.js, backend-luma/src/routes/worker.routes.js (POST /generation-jobs/recover-stale)
confidence: high

**Files:**
- `ai-engine/src/orchestration/pipeline/resume.js`
- `src/orchestration/queue/lease.js`
- `backend-luma/src/routes/worker.routes.js (POST /generation-jobs/recover-stale)`

## Auth lifecycle
**Trigger:** register/login/logout, refresh tokens, email verify, password reset.
*[[luma]] · confidence: medium*

trigger: register/login/logout, refresh tokens, email verify, password reset.
steps: express-validator/joi schemas → bcrypt hash → JWT access + refresh tokens (refreshtoken model) → RBAC roles gate admin/superadmin routers; login rate-limited.
files: backend-luma/src/routes/auth.routes.js, src/services/auth.service.js, src/middlewares/authMiddlewares.js
confidence: medium-high

**Files:**
- `backend-luma/src/routes/auth.routes.js`
- `src/services/auth.service.js`
- `src/middlewares/authMiddlewares.js`
