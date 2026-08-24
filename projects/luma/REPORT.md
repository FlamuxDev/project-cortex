# CORTEX REPORT — Luma

## META
- project_id: luma
- root: /home/aboud/Dev/Luma
- kind: full-stack AI SaaS platform (3 independent services + root dev orchestrator; explicitly NOT an npm workspace — root `package.json` states each service keeps its own deps)
- languages: JavaScript (ESM in ai-engine, CommonJS in backend), JSX, SQL, Prisma schema DSL; TypeScript only as a typecheck layer over JS (`ai-engine/tsconfig.json`)
- frameworks: Express 5 + Sequelize 6 + Swagger (backend-luma); Node 20 worker + Prisma 6 + Zod + Pino (ai-engine); React 19 + Vite 8 + react-router 7 + axios (LUMA_FontEnd)
- package_managers: npm (3 separate lockfiles + root)
- test_frameworks: Jest + Supertest (backend), Vitest (ai-engine; ~90 colocated unit tests + integration suite), none for frontend
- deployment: Docker Compose (backend + redis + nginx + certbot; Postgres on host) with PM2 inside container or on host; GHCR images via GitHub Actions CD (`backend-luma/README.md`); worker is a plain node process (`npm run worker`)

## OVERVIEW

Luma ("Luma Architect") turns a raw software idea into a complete engineering blueprint using a multi-agent "council": 11 seeded agents named after computing pioneers (lovelace, turing, hopper, brooks, diffie, grove, norman, torvalds, codd, fielding, knuth) generate blueprint sections and Mermaid diagrams, debate/review each other's output, and Knuth compiles the final document. Root docs confirm scope: `LUMA_ARCHITECT_GRADUATION_PROJECT_1_DOCUMENTATION.md` ("AI-Powered Multi-Agent Software Engineering Blueprint Platform", a university graduation project, analysis/design phase). The product domain is api.luma-agent.com (hardcoded default in `LUMA_FontEnd/src/api/api.js:3`).

Three services under one git repo. `backend-luma` is the client-facing REST API (auth/JWT/RBAC, blueprints, sections, diagrams, exports, SSE events) plus a dedicated machine surface `/api/worker/v1` implementing the 31-operation worker contract. `ai-engine` is the background orchestration worker that claims jobs from a Postgres-backed queue (`generation_jobs`) and drives agents through providers (OpenAI-compatible / Gemini / mock) with validation gates. `LUMA_FontEnd` is the React SPA (landing, auth, workspace, live blueprint viewer over SSE, admin pages).

A notable architectural pivot is visible in the docs: the worker originally wrote directly to the shared PostgreSQL database (`DATA_SOURCE=prisma`, still tested); it now defaults to `DATA_SOURCE=backend`, reaching all data through Backend REST per `ai-engine/contracts/worker-backend-api.v1.yaml`. `ai-engine/docs/worker-contract.md` claims the backend side "is not implemented yet", but `backend-luma/src/routes/worker.routes.js` implements exactly those 31 endpoints with fencing semantics — the doc appears stale relative to the `integration-final` branch [inferred].

## ARCHITECTURE

- **Process topology**: root `dev-all.js` spawns backend (`npm run dev`, :3000), frontend (Vite), then polls backend HTTP readiness before starting the ai-engine worker — because the worker exits if the backend is unreachable and nodemon only restarts on file change (`dev-all.js:10-13`). Requires pre-running Postgres/Redis containers.
- **Entry points**: `backend-luma/src/server.js` (Express bootstrap → loaders → :3000, swagger at `/api-docs`); `ai-engine/src/worker/index.js` (poll loop, `--once` mode, operational HTTP server `src/worker/operational-server.js` for health/metrics); `LUMA_FontEnd/src/main.jsx`.
- **Boundaries**:
  - Frontend → Backend only; never calls the worker directly (`ai-engine/docs/architecture.md` Scope).
  - Worker → data via one port interface `ai-engine/src/data/port.js`; two adapters: `prisma-data-source.js` (direct PG, SKIP LOCKED claims, fenced writes) and `backend-data-source.js` (REST, default). Orchestration code never touches DB/HTTP clients directly.
  - Live updates: Backend SSE stream `GET /api/blueprints/:id/events` (`blueprintEvent.route.js`); in prisma mode events arrive via `pg_notify('blueprint_events')`.
- **Backend layering**: routes → controllers → services → repositories → Sequelize models, plus loaders/middlewares/validations/locales (`backend-luma/src/` layout).
- **Worker pipeline**: queue claim/lease → job dispatch (`handleJob`: generate | retry | regenerate_section) → workflow-builder topological batches → context-manager budgets → provider adapters → validation gates → sectioner persistence → events publish.
- **Contracts as code**: `contracts/worker-backend-api.v1.yaml` (31 ops) mirrored in both services; `ai-engine/scripts/generate-worker-schema-contract.mjs --check` enforces schema contract (`test:contract`).

## MODULES

### backend-api — Express REST service
purpose: client-facing API: auth (JWT access+refresh, email verification, password reset), users/roles, admin & superadmin surfaces, blueprints CRUD + retry/cancel, sections, diagrams, agent runs/messages (client view), PDF exports (pdfkit), audit/security logs, SSE event stream, and the fenced `/api/worker/v1` surface.
path_prefixes: backend-luma/src/
key_files: src/app.js, src/loaders/routes.loader.js, src/routes/blueprint.routes.js, src/routes/worker.routes.js, src/services/blueprintEvent.service.js
entrypoints: src/server.js (nodemon/pm2/docker)
responsibilities: validation (express-validator + joi), rate limiting, helmet/CORS/compression, i18n locales, swagger docs, Sequelize migrations/seeders.
invariants: worker surface must not be merged with client-facing endpoints — it carries lease fencing + transactional guarantees (`worker.routes.js:6-11`).
pitfalls: `.env` holds real secrets locally (gitignored); Redis role beyond rate limiting not fully traced [uncertain].
confidence: high

### ai-worker — Agent orchestration engine
purpose: background worker that claims generation jobs, materializes one AgentRun per council agent, executes them in dependency batches through LLM providers, validates output, persists sections/diagrams/messages, and settles jobs truthfully.
path_prefixes: ai-engine/src/
key_files: src/worker/index.js, src/worker/generate-job.js, src/orchestration/pipeline/workflow-builder.js, src/orchestration/pipeline/scheduler.js, src/orchestration/pipeline/run-agent.js, src/orchestration/providers/resilient-provider.js, src/orchestration/validation/core.js, prisma/seed.js
entrypoints: npm run worker[:dev|:once]; playground/injection/regression scripts in scripts/
responsibilities: lease renewal + stale recovery, heartbeat, metrics, drain/shutdown signals, token accounting, retry policies, provenance CLI (`scripts/provenance-cli.mjs`).
invariants: state machines are closed — Job `queued→running→completed|failed|cancelled`; unsupported job types must fail, never pass through (`UnsupportedJobTypeError`, index.js:27); final settlement is compare-and-set so late cancellations can't be overwritten.
pitfalls: exits at startup when backend unreachable (by design); validator set (brooks/diffie/grove/norman/torvalds…) is mid-refactor on the dirty tree.
confidence: high

### data-port — storage abstraction inside ai-engine
purpose: single data-access interface making storage a deployment choice; every multi-row atomic unit maps to exactly one port operation.
path_prefixes: ai-engine/src/data/
key_files: src/data/port.js, src/data/backend-data-source.js, src/data/prisma-data-source.js, src/data/http-client.js
entrypoints: getDataSource() from src/data/index.js
responsibilities: CAS ops return booleans instead of throwing (lost races are normal); bearer auth, bounded retries for idempotent calls only.
invariants: one request = one transaction on the backend adapter; `(workerId, leaseGeneration)` fencing token verified on renew/settle to stop zombie workers.
pitfalls: HTTP cannot span transactions — this forces coarse non-CRUD endpoints (documented tradeoff).
confidence: high

### frontend-spa — React client
purpose: landing page, auth flows (register/login/verify/reset), workspace dashboard, live blueprint creation/viewer with SSE progress, admin console (Users, Logs, SystemState, Settings, Overview).
path_prefixes: LUMA_FontEnd/src/
key_files: src/App.jsx, src/api/api.js, src/page/new-blueprint.jsx, src/page/Workspace.jsx, src/i18n.jsx
entrypoints: vite dev server; routes in App.jsx (/login, /Work, /new-blueprint, /newblueprint2, /DualWorkspace, admin paths)
responsibilities: axios instance with token interceptor (accessToken w/ legacy `token` fallback), EventSource subscription to blueprint events (new-blueprint.jsx:2578), markdown rendering (react-markdown + remark-gfm), dark mode toggle.
invariants: talks only to backend base URL `VITE_API_URL || https://api.luma-agent.com/api`.
pitfalls: token in localStorage + console.logs of auth headers (api.js:30-58); no tests; mega-components (new-blueprint.jsx >2,500 lines).
confidence: high

### db-schema — shared PostgreSQL schema
purpose: canonical platform schema owned by BE team; ai-engine keeps a runnable worker-scoped subset (`ai-engine/prisma/schema.prisma` header, Arabic comments).
path_prefixes: backend-luma/src/models/, backend-luma/src/migrations/, ai-engine/prisma/
key_files: ai-engine/prisma/schema.prisma, ai-engine/prisma/migrations/*/migration.sql (5), luma_backup.sql
entrypoints: `db:migrate*` scripts both sides
responsibilities: entities documented under DATABASE below; CHECK constraints added by manual BE migrations where Prisma can't express them.
invariants: migration history must never be gitignored again (see GIT LESSONS, 40632ac).
pitfalls: `blueprint_sections.status` model default `"completed"` is rejected by the DB CHECK (`generated|edited|approved`) — latent trap documented in schema.prisma:172-176.
confidence: high

### contracts-and-prompts — integration boundary + prompt assets
purpose: machine-readable worker/backend contract and versioned prompt blocks/checks/drafts for the agent council.
path_prefixes: ai-engine/prompts/, ai-engine/contracts/, backend-luma/contracts/, ai-engine/docs/
key_files: contracts/worker-backend-api.v1.yaml, contracts/worker-schema-contract.v1.json, prompts/README.md, prompts/blocks/, docs/worker-contract.md, docs/architecture.md
entrypoints: contract check via npm run test:contract
responsibilities: cross-team change review requirement; provenance docs (docs/provenance.md); runbooks + capacity benchmark docs.
invariants: contract changes require review by both owners (worker-contract.md).
confidence: high

### quality-infra — evaluation & benchmarks
purpose: mutation-suite evaluator, injection corpus (prompt-injection resistance), regression runner with runtime budget, capacity smoke/matrix benchmarks.
path_prefixes: ai-engine/quality/, ai-engine/tests/, ai-engine/scripts/
key_files: quality/evaluator/evaluate.js, scripts/run-injection-corpus.js, scripts/run-regression.js, scripts/benchmark/runner/run-smoke.js
entrypoints: npm run quality:pilot | regression | injection | capacity:smoke | capacity:full
confidence: medium

## FLOWS

### Blueprint generation (end-to-end)
trigger: user submits idea on /new-blueprint (frontend) → POST /api/blueprints creates Blueprint (+BlueprintSettings) and a `generation_jobs` row (job_type=generate, status=queued).
steps: (1) worker claims oldest queued job atomically — `FOR UPDATE SKIP LOCKED` + fenced update (prisma mode) or claim endpoint (backend mode) — stamps `(workerId, leaseGeneration)`; (2) loads Blueprint + mandatory settings (DB values authoritative over payload copies); (3) workflow-builder loads active AgentDefinitions, applies security/devops skips, builds topological batches; (4) materializes one real AgentRun per agent (pending resumes, completed reused, non-stale duplicates fail closed); (5) per batch, context manager picks approved upstream output within budgets; provider adapter calls OpenAI/Gemini/mock; (6) output passes agent validators + canary leak filter + Mermaid gate (LUMA-212); (7) sectioner appends section revisions + diagrams atomically with their event message; (8) Knuth compiles final document; job settled via compare-and-set; (9) blueprint → completed; SSE pushes progress to viewer.
files: ai-engine/src/worker/generate-job.js, src/orchestration/pipeline/{scheduler,sectioner,workflow-builder}.js, src/orchestration/events/publish.js, backend-luma/src/controllers/worker.controller.js, LUMA_FontEnd/src/page/new-blueprint.jsx
confidence: high

### Live progress streaming (SSE)
trigger: frontend opens EventSource on GET /api/blueprints/:id/events after starting generation.
steps: backend subscribes to blueprint events (pg_notify in prisma mode / written event rows otherwise) and streams to authenticated client; viewer renders sections/diagrams incrementally.
files: backend-luma/src/services/blueprintEvent.service.js, src/routes/blueprintEvent.route.js, LUMA_FontEnd/src/page/new-blueprint.jsx
confidence: high

### Stale-job recovery
trigger: worker heartbeat/lease expiry or explicit recover endpoint.
steps: stale leased job requeued inside the same serializable transaction that flips its running AgentRuns back to pending and increments retry_count; resume restricted to the stuck job's own runs via generation_job_id (LUMA-172).
files: ai-engine/src/orchestration/pipeline/resume.js, src/orchestration/queue/lease.js, backend-luma/src/routes/worker.routes.js (POST /generation-jobs/recover-stale)
confidence: high

### Auth lifecycle
trigger: register/login/logout, refresh tokens, email verify, password reset.
steps: express-validator/joi schemas → bcrypt hash → JWT access + refresh tokens (refreshtoken model) → RBAC roles gate admin/superadmin routers; login rate-limited.
files: backend-luma/src/routes/auth.routes.js, src/services/auth.service.js, src/middlewares/authMiddlewares.js
confidence: medium-high

## APIS

Base: http://localhost:3000 (dev), swagger at /api-docs.

| Prefix | Method(s) | Purpose |
|---|---|---|
| /health | GET | liveness |
| /api/auth/* | POST | register, login, logout, refresh, forgot/reset password, verify |
| /api/users | CRUD-ish | user profile management |
| /api/admin, /api/super-admin | mixed | admin/superadmin consoles |
| /api/blueprints | GET, POST, GET/:id, PATCH/:id, DELETE/:id | blueprint CRUD |
| /api/blueprints/retry/:id, /:id/cancel | POST | generation control |
| /api/blueprints/:id/events | GET (SSE) | live event stream |
| /api (sections) | mixed | blueprint sections |
| /api (agents, diagrams, exports) | mixed | agent defs, diagrams, PDF export files |
| /api/agent-runs, /api/agent-messages | mixed | client-view of runs/messages |
| /api/worker/v1/generation-jobs/* | POST/GET | claim, oldest-queued, recover-stale, get, lease-renew, status transition |
| /api/worker/v1/blueprints/:id(+status), .../agent-runs/materialize, etc. | GET/PATCH/POST | remaining ~25 fenced worker ops (31 total per contract) |

## DATABASE

PostgreSQL 16 (host-managed; docker compose only for backend/redis/nginx/certbot). Two ORM layers over the same DB: Sequelize (backend, source of truth migrations) and Prisma (worker subset). Entities:

- users / roles / refresh_tokens / password_reset_tokens — identity, RBAC, sessions; soft delete (deleted_at), is_active flag
- blueprints — user idea (idea_text, project_type, complexity, output_language), status enum draft|generating|in_review|waiting_for_review|completed|failed
- blueprint_settings — 1:1 toggles (diagrams/security/devops, detail_level, ai_model, extra_instructions)
- agent_definitions — the council: code_name unique, system_prompt, execution_order 1..11, is_active
- agent_runs — one per agent execution; input/output context, tokens_used, retry_count, optional generation_job_id for recovery scoping
- agent_messages — inter-agent traffic (status|debate|review|resolution) with sender/target agent
- blueprint_sections — versioned content_markdown rows, unique (blueprint, section_key, version), status CHECK generated|edited|approved
- diagrams — mermaid_code, diagram_type, versioned, optional section link
- reviews — reviewer agent vs target section (severity, open/closed) feeding the debate subsystem
- generation_jobs — the queue: job_type generate|retry|regenerate_section, attempts, locked_at, worker_id + lease_generation fencing token, recovery_count, payload_json; claimed via FOR UPDATE SKIP LOCKED
- system_settings, audit_logs — platform config; failover/context-truncation incidents (worker writes with ip_address='worker')
- worker_heartbeats — liveness of workers (backend model list)

Note: root `luma_backup.sql` is a UTF-16 pg_dump whose dump also contains an unrelated clinic schema (appointment, doctor, patient, clinic_manager, time_slot…) alongside public.luma tables — likely dumped from a shared dev instance [inferred]. Treat as backup artifact, not schema source.

## TESTS

- backend-luma: Jest + Supertest. Commands: `npm test`, `test:unit`, `test:integration`, `test:contract` (+ `test:contract:verify`), `test:coverage`. Suites in tests/unit (env/setup), tests/integration (~20 files: auth.security, security-logs, worker-queue, worker-agent-runs, worker-messages-sections-reviews, response-contracts, blueprint-events, middlewares, repositories…).
- ai-engine: Vitest. `npm test` runs ~90 colocated unit tests across src/; `test:integration` (tests/, singleFork pool against real PG: backend-mode-e2e, multi-process worker, regenerate-section); `test:contract` checks generated schema contract; plus `quality:pilot` (mutation suite), `regression`, `injection` corpus, `capacity:smoke/full` benchmarks.
- LUMA_FontEnd: no test framework found (eslint + prettier only).

## GIT LESSONS

- 44dfceb "feat: complete LUMA project" (Aug 8) — big-bang initial publish; history effectively starts there, everything before is unrecorded.
- Ticket discipline: fix/LUMA-207…218 branches merged individually with scoped commits (e.g. 60563fc integrates 207/210/212-214/216-218 but held back the workflow file needing OAuth 'workflow' scope) — good example of splitting blocked CI changes out.
- 40632ac: `.gitignore`'s `*.sql` rule silently dropped Prisma migration history — lesson: broad ignore patterns can eat required artifacts; fixed by force-tracking migrations.
- 74c2b17: closed drift between schema.prisma and migration history — keep ORM schema and migrations reconciled deliberately.
- a9e3a90: resolving react-hooks lint findings surfaced "3 real wiring bugs" — lint-as-bug-finder, not bureaucracy.
- c137f74: workspace dashboard and blueprint viewer were mock UI first, made "real" later — staged realism during integration.
- da7bced: root dev:all script encodes an operational lesson in comments — worker/backend startup race (parallel start loses; poll HTTP before spawning worker).
- Current state: `integration-final` carries ~29 modified files uncommitted (+2181/−251: validators, provider adapters, sectioner, agent.service, Workspace/new-blueprint pages) — integration work exists only in working tree.
- Many `worktree-agent-*` local branches — parallel automated agent sessions left behind.

## DECISIONS

- Worker decoupled from storage via a single port + two adapters; default flipped from direct DB to Backend API mode (architecture.md, worker-contract.md).
- Multi-row atomicity pushed into coarse endpoints ("one request is one transaction"); lost races are `200 {"applied": false}`, never errors (worker-contract.md rules).
- Lease fencing token `(worker_id, lease_generation)` set atomically at claim and re-verified at renew/settle to neutralize zombie workers (schema.prisma GenerationJob comments; migration 20260802105804_lease_ownership_fencing).
- Schema ownership split: BE owns platform schema; ai-engine maintains a runnable worker-scoped subset, coordinated via docs/worker-contract.md (schema.prisma header).
- Graceful degradation: failed upstream dependency blocks transitive downstream except Knuth, which compiles an explicitly degraded document (architecture.md).
- CAS booleans over exceptions for race-prone queue operations.
- Council config lives in DB (agent_definitions seeded, execution_order 1..11), not code — prompts editable without deploys [inferred from seed].
- Deliberate gaps accepted and documented: debate coordinator not yet wired into generate path; provider failover health policy unwired (architecture.md "Deliberate gaps").
- Deployment simplicity: Docker Compose + PM2, Postgres kept on host outside compose (README).

## RISKS & TECH DEBT

- ~29 dirty files uncommitted on integration-final touching core validation/adapters/frontend wiring — unmerged integration state, easy to lose.
- Doc/code drift: worker-contract.md says backend hasn't implemented the worker API; worker.routes.js implements all 31 ops — docs lag branch reality [uncertain which is authoritative].
- Frontend: tokens in localStorage, console.log of auth headers (api.js), zero tests, 2,500+-line page components, duplicated blueprint pages (new-blueprint vs newblueprint2).
- Default production URL hardcoded in frontend bundle (api.luma-agent.com).
- Untracked `LUMA_FontEnd/.env` sitting in tree.
- Latent trap: invalid `status` default on blueprint_sections rejected by DB CHECK only at write time.
- Debate subsystem built and tested but dead code in the main path; same for provider failover health policy — maintenance burden until wired or cut.
- luma_backup.sql mixes foreign clinic schema; UTF-16 encoding makes tooling awkward.
- Backend-mode e2e proven only against a stub server, never the live backend (per docs) — the flagship decoupling path has thin real-world evidence.
- Single dominant committer (ABOUD, 28 of ~50 commits) — bus factor.
- Graduation doc contains placeholder fields ([Student Name]) — deliverable incomplete.

## UNCERTAIN

- Whether DATA_SOURCE=backend works against the deployed backend in anger (stub-only evidence).
- Redis usage breadth (rate limiting confirmed; sessions/cache assumed) [inferred].
- Exact TS involvement in ai-engine (typecheck-only over JS assumed).
- Which service owns the SSE event fan-out in backend mode (event rows vs notify) — read partially traced.
- Origin/intent of the clinic tables in luma_backup.sql.
- Runtime status of the uncommitted validator refactor (tests modified alongside suggest mid-flight work).
