---
cortex-generated: true
title: cvm flows
tags: [flows/project]
---

# CVM — Product Flows

End-to-end behaviors as verified from source. Files are the evidence trail.

## Ingestion → quarantine → replay
**Trigger:** POST /v1/ingest/{source_code} batch upload or scheduled connector pull
*[[cvm]] · confidence: verified*

trigger: POST /v1/ingest/{source_code} batch upload or scheduled connector pull
steps: 1. contract validation per data_contract 2. accepted rows → partitioned customer_event append-only log; bad rows → ingestion_error/quarantine with reasons 3. quality detections update data_quality_metric 4. duplicates counted on batch (0 accepted/25 dup) 5. replay from quarantine screen
files: packages/modules/src/ingestion/**, migrations 0005/0006/0007, e2e/golden-path.spec.ts:361,531
confidence: verified

**Files:**
- `packages/modules/src/ingestion/**`
- `migrations 0005/0006/0007`
- `e2e/golden-path.spec.ts:361`
- `531`

## Identity resolve → merge/unmerge → C360 reprojection
**Trigger:** ingestion of identifiers; manual conflict resolution; POST /v1/identity/merge|unmerge
*[[cvm]] · confidence: verified*

trigger: ingestion of identifiers; manual conflict resolution; POST /v1/identity/merge|unmerge
steps: 1. deterministic resolution; ambiguity raises identity_conflict (queue) 2. merge writes identity_merge + link events and publishes identity.changed OUTBOX ROW IN SAME TXN 3. maintenance outbox.relay delivers to worker 4. worker maps ALL THREE payload ids → enqueueProfileProjection 5. idempotent projector rebuilds both profiles from restored graph
files: apps/worker/src/main.ts:51-71, packages/modules/src/identity/application/merge.ts, packages/modules/src/profile/application/project.ts, e2e golden-path "merge reprojects both customers"
confidence: verified

**Files:**
- `apps/worker/src/main.ts:51-71`
- `packages/modules/src/identity/application/merge.ts`
- `packages/modules/src/profile/application/project.ts`
- `e2e golden-path "merge reprojects both customers"`

## Audience build → materialise → explain
**Trigger:** UI rule builder (AST in URL) → POST /v1/segments; schedule
*[[cvm]] · confidence: verified*

trigger: UI rule builder (AST in URL) → POST /v1/segments; schedule
steps: 1. validate AST vs closed field catalogue 2. preview count estimate 3. compile preferring feature read-model, parameterised SQL 4. exclusions subtract provably 5. segment_run materialises membership 6. explain walks same AST for one customer
files: packages/modules/src/segments/application/*.ts, docs/rule-ast.md, e2e:1094,1348
confidence: verified

**Files:**
- `packages/modules/src/segments/application/*.ts`
- `docs/rule-ast.md`
- `e2e:1094`
- `1348`

## Offer approve → decision (gate+rank) → NO_ACTION possible
**Trigger:** POST /v1/decisions (or /batch ≤500)
*[[cvm]] · confidence: verified*

trigger: POST /v1/decisions (or /batch ≤500)
steps: 1. candidates from catalog 2. customer-half gate checks 1-4 once 3. per-offer checks 5-7 (eligibility/inventory/campaign conflict) 4. ranker = pure fn over survivors, score via ScoreProvider (online fresh else batch floor) 5. select top or NO_ACTION with denial codes 6. reserve capacity conditionally 7. persist decision + EVERY candidate with denial code + policy version
files: packages/modules/src/decision/application/gate.ts, decide.ts, rank.ts, http/routes.ts:127, e2e:1453,1748
confidence: verified

**Files:**
- `packages/modules/src/decision/application/gate.ts`
- `decide.ts`
- `rank.ts`
- `http/routes.ts:127`
- `e2e:1453`
- `1748`

## Campaign approve → run → deliver (effectively-once) → receipts → funnel
**Trigger:** campaign launch (requires approval + typed confirm)
*[[cvm]] · confidence: verified*

trigger: campaign launch (requires approval + typed confirm)
steps: 1. freeze audience snapshot into campaign_target 2. run creates delivery jobs 3. CLAIM delivery_attempt row ON CONFLICT DO NOTHING RETURNING unique (tenant_id,dedupe_key) BEFORE provider call 4. PolicyGate RE-EVALUATED per send (consent withdrawn post-approval ⇒ suppressed) 5. adapter raw-HTTP send w/ dedupe key as idempotency key 6. receipt webhook updates state machine idempotently 7. kill switch cancels remaining targets 8. funnel snapshot reconciles vs raw
files: packages/modules/src/delivery/application/send.ts, infrastructure/adapters.ts, packages/modules/src/campaigns/**, apps/api/__tests__/delivery-idempotency.int.test.ts, e2e:1867,2264
confidence: verified

**Files:**
- `packages/modules/src/delivery/application/send.ts`
- `infrastructure/adapters.ts`
- `packages/modules/src/campaigns/**`
- `apps/api/__tests__/delivery-idempotency.int.test.ts`
- `e2e:1867`
- `2264`

## §39 end-to-end trace
**Trigger:** GET /v1/trace/{deliveryId}; console /trace/[id]
*[[cvm]] · confidence: verified*

trigger: GET /v1/trace/{deliveryId}; console /trace/[id]
steps: joins campaign_run → profile → feature values (with def versions) → decision + all candidates/denials → model registry → delivery_attempt → receipts → engagement/conversions; each link states present-or-why-absent; correlation id joins audit
files: packages/modules/src/delivery/application/trace.ts, apps/web/src/app/(app)/trace/[id]/page.tsx, e2e:2708
confidence: verified

**Files:**
- `packages/modules/src/delivery/application/trace.ts`
- `apps/web/src/app/(app)/trace/[id]/page.tsx`
- `e2e:2708`

## Governed ML lifecycle (Track B)
**Trigger:** pnpm ml:load-fixture → refresh-features → train; then API approve/deploy
*[[cvm]] · confidence: verified*

trigger: pnpm ml:load-fixture → refresh-features → train; then API approve/deploy
steps: 1. TS extractor pulls point-in-time features (occurred_at < as_of) via platform compiler 2. Python trains/evaluates offline, label = tenant-configured churn definition on dataset_snapshot 3. register model_version 4. SECOND PERSON approves (self refused) 5. deploy makes version live 6. nightly batch scoring writes customer_score w/ model_version_id; online provider computes fresh when deployed+features present 7. skew test replays trainer predictions to 1e-9 8. rollback operation audited
files: ml/src/cvm_ml/train.py, tools/ml/train.ts, packages/modules/src/ml/**, e2e:2371,2650
confidence: verified

**Files:**
- `ml/src/cvm_ml/train.py`
- `tools/ml/train.ts`
- `packages/modules/src/ml/**`
- `e2e:2371`
- `2650`

## Right to erasure
**Trigger:** POST /v1/erasure-requests → approval
*[[cvm]] · confidence: strongly_inferred*

trigger: POST /v1/erasure-requests → approval
steps: 1. scope query (/erasure-scope) 2. remove personal payload KEYS ONLY through narrow append-only path 3. profile reprojected 4. audit_event intact 5. aggregates unmoved 6. quarantined rows substring-matched [limitation]
files: packages/modules/src/privacy/**, migration 0013_erasure, e2e:2786,2919
confidence: strongly_inferred

**Files:**
- `packages/modules/src/privacy/**`
- `migration 0013_erasure`
- `e2e:2786`
- `2919`
