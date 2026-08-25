---
cortex-generated: true
title: luma api
tags: [api/project]
---

# Luma — API Surface

128 routes. Grouped by owning file; every route names its handler.

## `LUMA_FontEnd/src/page/BlueprintsAdmen.jsx`
*module: [[luma/modules/React-Client|react-client]]*

- **GET** `/admin/blueprints`
- **GET** `/admin/blueprints` → {

## `LUMA_FontEnd/src/page/DualWorkspace.jsx`
*module: [[luma/modules/React-Client|react-client]]*

- **GET** `id`

## `LUMA_FontEnd/src/page/ForgotPassword.jsx`
*module: [[luma/modules/React-Client|react-client]]*

- **POST** `/auth/forgot-password` → {

## `LUMA_FontEnd/src/page/Login.jsx`
*module: [[luma/modules/React-Client|react-client]]*

- **POST** `/auth/login` → {

## `LUMA_FontEnd/src/page/Overview.jsx`
*module: [[luma/modules/React-Client|react-client]]*

- **GET** `/admin/blueprints?limit=10&sort=created_at:desc`

## `LUMA_FontEnd/src/page/Register.jsx`
*module: [[luma/modules/React-Client|react-client]]*

- **POST** `/auth/register` → {

## `LUMA_FontEnd/src/page/ResetPassword.jsx`
*module: [[luma/modules/React-Client|react-client]]*

- **POST** `/auth/reset-password` → {

## `LUMA_FontEnd/src/page/Resources.jsx`
*module: [[luma/modules/React-Client|react-client]]*

- **GET** `/blueprints?status=completed&limit=12`

## `LUMA_FontEnd/src/page/SystemState.jsx`
*module: [[luma/modules/React-Client|react-client]]*

- **GET** `/super-admin/system-stats`

## `LUMA_FontEnd/src/page/Users.jsx`
*module: [[luma/modules/React-Client|react-client]]*

- **GET** `/admin/users`

## `LUMA_FontEnd/src/page/VerifyEmail.jsx`
*module: [[luma/modules/React-Client|react-client]]*

- **POST** `/auth/resend-otp` → {
- **POST** `/auth/verify-otp` → {

## `LUMA_FontEnd/src/page/Workspace.jsx`
*module: [[luma/modules/React-Client|react-client]]*

- **GET** `/blueprints`

## `LUMA_FontEnd/src/page/newblueprint2.jsx`
*module: [[luma/modules/React-Client|react-client]]*

- **POST** `/auth/logout` → {
- **POST** `/blueprints` → payload
- **DELETE** `/users/account`
- **DELETE** `/users/account`
- **GET** `id`

## `ai-engine/src/worker/generate-job.js`
*module: [[luma/modules/Agent-Orchestration-Engine|agent-orchestration-engine]]*

- **GET** `hopper`
- **GET** `knuth`
- **GET** `turing`

## `backend-luma/src/app.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **USE** `/api-docs` → `swaggerUi`

## `backend-luma/src/loaders/express.loader.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **USE** `/api` → apiRateLimiter

## `backend-luma/src/loaders/routes.loader.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **GET** `/`
- **USE** `/api` → exportFileRoutes
- **USE** `/api` → diagramRoutes
- **USE** `/api` → agentRoutes
- **USE** `/api` → sectionRoutes
- **USE** `/api/admin` → adminRoutes
- **USE** `/api/agent-messages` → agentMessageRoutes
- **USE** `/api/agent-runs` → agentRunRoutes
- **USE** `/api/auth` → authRoutes
- **USE** `/api/blueprints` → blueprintEventRoutes
- **USE** `/api/blueprints` → blueprintRoutes
- **USE** `/api/super-admin` → superAdminRoutes
- **USE** `/api/users` → userRoutes
- **USE** `/api/worker/v1` → workerRoutes
- **GET** `/health`

## `backend-luma/src/middlewares/rateLimiterMiddlewares.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **GET** `x-rate-limit-test`

## `backend-luma/src/routes/admin.routes.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **GET** `/blueprints` → adminController.getBlueprints
- **GET** `/logs` → adminController.getLogs
- **GET** `/users` → adminController.getUsers
- **PATCH** `/users/:id/status` → adminController.updateUserStatus

## `backend-luma/src/routes/agent.routes.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **GET** `/blueprints/:id/agents-status` → agentController.getStatus
- **POST** `/blueprints/:id/generate` → agentController.generate
- **POST** `/blueprints/:id/retry` → agentController.retry

## `backend-luma/src/routes/agentMessage.routes.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **POST** `/` → agentMessageController.create
- **DELETE** `/:id` → agentMessageController.delete
- **GET** `/:id` → agentMessageController.getById
- **GET** `/blueprint/:id` → agentMessageController.getByBlueprint

## `backend-luma/src/routes/agentRun.routes.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **GET** `/:id` → agentRunController.getById
- **PATCH** `/:id/complete` → agentRunController.complete
- **PATCH** `/:id/fail` → agentRunController.fail
- **PATCH** `/:id/retry` → agentRunController.retry
- **PATCH** `/:id/start` → agentRunController.start
- **GET** `/pending` → agentRunController.getPending

## `backend-luma/src/routes/auth.routes.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **POST** `/forgot-password` → passwordResetController.forgotPassword
- **POST** `/login` → authController.login
- **POST** `/logout` → authController.logout
- **POST** `/refresh-token` → authController.refreshAccessToken
- **POST** `/register` → authController.register
- **POST** `/resend-otp` → passwordResetController.resendOtp
- **POST** `/reset-password` → passwordResetController.resetPassword
- **POST** `/verify-otp` → passwordResetController.verifyOtp

## `backend-luma/src/routes/blueprint.routes.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **GET** `/` → blueprintController.getAll
- **POST** `/` → blueprintController.create
- **DELETE** `/:id` → blueprintController.delete
- **PATCH** `/:id` → blueprintController.update
- **GET** `/:id` → blueprintController.getById
- **POST** `/:id/cancel` → blueprintController.cancel
- **POST** `/retry/:id` → blueprintController.retry

## `backend-luma/src/routes/blueprintEvent.route.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **GET** `/:id/events` → blueprintEventController.stream

## `backend-luma/src/routes/diagram.routes.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **GET** `/blueprints/:id/diagrams` → diagramController.getAll
- **POST** `/blueprints/:id/diagrams` → diagramController.create
- **DELETE** `/diagrams/:id` → diagramController.delete
- **PATCH** `/diagrams/:id` → diagramController.update
- **GET** `/diagrams/:id` → diagramController.getById

## `backend-luma/src/routes/exportFile.routes.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **GET** `/blueprints/:id/exports` → exportFileController.getAll
- **POST** `/blueprints/:id/exports` → exportFileController.create
- **DELETE** `/exports/:exportId` → exportFileController.delete
- **GET** `/exports/:exportId` → exportFileController.getById
- **GET** `/exports/:exportId/download` → exportFileController.download

## `backend-luma/src/routes/section.routes.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **GET** `/blueprints/:id/sections` → sectionController.getAll
- **PATCH** `/blueprints/:id/sections/:sectionId` → sectionController.update

## `backend-luma/src/routes/superadmin.routes.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **GET** `/blueprints` → adminController.getBlueprints
- **GET** `/logs` → adminController.getLogs
- **PUT** `/system-settings` → superAdminController.updateSystemSettings
- **GET** `/system-stats` → superAdminController.getSystemStats
- **GET** `/users` → adminController.getUsers
- **DELETE** `/users/:id` → superAdminController.deleteUser
- **PATCH** `/users/:id/role` → superAdminController.updateUserRole
- **PATCH** `/users/:id/status` → adminController.updateUserStatus
- **PATCH** `/users/:id/status` → adminController.updateUserStatus

## `backend-luma/src/routes/user.routes.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **DELETE** `/account` → userController.deleteAccount
- **PATCH** `/account/activate` → userController.activateAccount
- **PATCH** `/account/deactivate` → userController.deactivateAccount

## `backend-luma/src/routes/worker.routes.js`
*module: [[luma/modules/Express-Rest-Service|express-rest-service]]*

- **GET** `/agent-definitions` → workerController.listActiveAgentDefinitions
- **POST** `/agent-messages` → workerController.publishEvent
- **POST** `/agent-runs` → workerController.createAgentRun
- **GET** `/agent-runs` → workerController.listAgentRuns
- **GET** `/agent-runs/:runId` → workerController.getAgentRun
- **POST** `/agent-runs/:runId/begin-retry` → workerController.beginAgentRunRetry
- **PATCH** `/agent-runs/:runId/output` → workerController.updateAgentRunOutput
- **POST** `/agent-runs/:runId/recover` → workerController.recoverAgentRun
- **POST** `/agent-runs/:runId/transition` → workerController.transitionAgentRun
- **POST** `/agent-runs/skip-pending` → workerController.skipPendingAgentRuns
- **POST** `/audit-logs` → workerController.createAuditLog
- **GET** `/audit-logs` → workerController.listAuditLogs
- **GET** `/audit-logs/count` → workerController.countAuditLogs
- **GET** `/blueprints/:blueprintId` → workerController.getBlueprint
- **POST** `/blueprints/:blueprintId/agent-runs/materialize` → workerController.materializeAgentRuns
- **POST** `/blueprints/:blueprintId/sections` → workerController.createSectionVersion
- **GET** `/blueprints/:blueprintId/sections/:sectionKey/latest` → workerController.getLatestSection
- **GET** `/blueprints/:blueprintId/sections/:sectionKey/oldest` → workerController.getOldestSection
- **POST** `/blueprints/:blueprintId/sections/persist` → workerController.persistAgentOutput
- **PATCH** `/blueprints/:blueprintId/status` → workerController.setBlueprintStatus
- **GET** `/generation-jobs/:jobId` → workerController.getJob
- **POST** `/generation-jobs/:jobId/lease` → workerController.renewJobLease
- **POST** `/generation-jobs/:jobId/status` → workerController.transitionJobStatus
- **POST** `/generation-jobs/claim` → workerController.claimNextJob
- **GET** `/generation-jobs/oldest-queued` → workerController.getOldestQueuedJobCreatedAt
- **POST** `/generation-jobs/recover-stale` → workerController.recoverStaleJobs
- **POST** `/reviews` → workerController.createReview
- **POST** `/reviews/:reviewId/resolve` → workerController.applyReviewResolution
- **GET** `/reviews/leak` → workerController.findLeakReview
- **POST** `/reviews/leak-findings` → workerController.persistLeakFindings
- **PUT** `/worker-heartbeat` → workerController.updateWorkerHeartbeat
