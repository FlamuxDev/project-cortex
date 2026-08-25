---
cortex-generated: true
title: telvora flows
tags: [flows/project]
---

# Telvora — Product Flows

End-to-end behaviors as verified from source. Files are the evidence trail.

## Self-service signup → first Tenant Admin
**Trigger:** visitor submits POST /api/v1/auth/signup {organizationName, ownerEmail} (public)
*[[telvora]] · confidence: verified*

trigger: visitor submits POST /api/v1/auth/signup {organizationName, ownerEmail} (public)
steps:
1. Rate-limited 5/hr/IP (reused leads.RateLimiter, ADR-0005)
2. CreateTenant with slug derived from org name + collision suffix; environment_label forced "sandbox"
3. Issue single-use invite account token bound to tenant-admin role; email invite link
4. Visitor lands on /invite/[token]; AcceptInvite sets password, verifies email, activates membership — zero new tables/tokens
files: internal/tenants/handler.go Signup, internal/auth/account_handler.go AcceptInvite, docs/adr/0005
confidence: verified

**Files:**
- `internal/tenants/handler.go Signup`
- `internal/auth/account_handler.go AcceptInvite`
- `docs/adr/0005`

## Batch ingestion → canonical model
**Trigger:** POST /api/v1/tenant/integrations/{id}/batch (or pull/webhook/stream)
*[[telvora]] · confidence: verified*

trigger: POST /api/v1/tenant/integrations/{id}/batch (or pull/webhook/stream)
steps:
1. Handler validates connector + permission; raw payload → FilesystemRawStore with SHA-256 manifest
2. Enqueue job on PostgresQueue (queue_message) with serialized tenant_id
3. Worker dequeues under telvora_worker pool; re-establishes tenant context; batch processor parses CSV/JSON
4. Mapping engine applies activated mapping version → canonical tables; failures → quarantine table
5. Data-quality detect/scores + lineage updated; incidents listed for remediation
files: internal/ingestion/{handler,worker,batch,rawstore}.go, internal/mapping/engine.go, internal/dataquality/
confidence: verified

**Files:**
- `internal/ingestion/{handler`
- `worker`
- `batch`
- `rawstore}.go`
- `internal/mapping/engine.go`
- `internal/dataquality/`

## Real-time decision (NBA-NBO)
**Trigger:** POST /api/v1/tenant/decisions {personId, ...} (authenticated, low-latency path)
*[[telvora]] · confidence: verified*

trigger: POST /api/v1/tenant/decisions {personId, ...} (authenticated, low-latency path)
steps:
1. Resolve tenant/person; build ContextSnapshot from feature values (degrades to stale/error chips, never fails)
2. Load eligible published offer versions; apply consent/suppression exclusions
3. Score candidates via deployed model versions (deterministic, no LLM); arbitrate winner
4. Persist decision with full trace (excluded candidates + versions kept); return recommendation
files: internal/decisions/store.go, handler.go:98; migration 0028_decision_engine
confidence: verified (store read; latency SLO claims from RELEASE_NOTES trusted as recorded measurements)

**Files:**
- `internal/decisions/store.go`
- `handler.go:98; migration 0028_decision_engine`

## Model training lifecycle (Go↔Python)
**Trigger:** model version created (optionally from template) → submit-approval → promote → train/score via ML_SERVICE_URL
*[[telvora]] · confidence: verified*

trigger: model version created (optionally from template) → submit-approval → promote → train/score via ML_SERVICE_URL
steps:
1. core-api resolves training population via segments.EvaluateVersion
2. HTTPMLClient POSTs /train {tenantId, modelVersionId, personIds, algorithm, taskType, windows, featureNames}
3. ml computes leakage-safe features from same Postgres (RLS-scoped), trains, writes artifact to local artifact dir, returns metrics/explanations
4. core-api persists metrics on model_version; worker sweeps drift/performance every 5min calling ml
files: internal/models/{ml_client,store,worker}.go, services/ml/app/main.py
confidence: verified

**Files:**
- `internal/models/{ml_client`
- `store`
- `worker}.go`
- `services/ml/app/main.py`

## Governed campaign execution
**Trigger:** campaign start after validation + approval gate
*[[telvora]] · confidence: strongly_inferred*

trigger: campaign start after validation + approval gate
steps:
1. Materialize segment members; consent evaluate per person/channel
2. Experiment bucketing assigns treatment/control (deterministic hash)
3. Dispatch via channel Registry adapter; callbacks recorded via public channel webhook
4. Kill/pause/resume manage runs; results computed as incremental value vs control
files: internal/campaigns/execution.go, internal/experiments/stats.go, internal/channels/registry.go
confidence: strongly_inferred (execution.go not fully read)

**Files:**
- `internal/campaigns/execution.go`
- `internal/experiments/stats.go`
- `internal/channels/registry.go`

## Journey execution
**Trigger:** TriggerRun or event_trigger node match; waits resumed by 2s scheduler worker
*[[telvora]] · confidence: strongly_inferred*

trigger: TriggerRun or event_trigger node match; waits resumed by 2s scheduler worker
steps:
1. Run created; steps persisted per node traversal
2. Split nodes re-derive branch from (runID,personID) deterministically
3. Channel actions dispatch; goal node terminates; kill supported
files: internal/journeys/{dag,execution,worker}.go
confidence: strongly_inferred

**Files:**
- `internal/journeys/{dag`
- `execution`
- `worker}.go`

## LLM converse (agentic draft)
**Trigger:** POST /api/v1/tenant/ai/converse
*[[telvora]] · confidence: strongly_inferred*

trigger: POST /api/v1/tenant/ai/converse
steps:
1. Policy check (tenant's allowed_models; default pins offline SimulatorProvider)
2. Runtime lets model call closed read-only tool registry (permission checked per tool)
3. Redaction pass before external providers; conversation + tool calls persisted for audit
files: internal/llm/{runtime,tools,redact}.go
confidence: strongly_inferred

**Files:**
- `internal/llm/{runtime`
- `tools`
- `redact}.go`
