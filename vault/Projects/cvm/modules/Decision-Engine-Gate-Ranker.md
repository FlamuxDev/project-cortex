---
cortex-generated: true
title: decision-engine-gate-ranker
tags: [module]
---

# decision engine (gate + ranker)

**Project:** [[cvm]] | **Confidence:** verified | **verified@** `2d7ffcee167d`
**Owns:** `packages/modules/src/decision/`

purpose: PRD §21 eleven-step NBA: candidates from catalog → eligibility/policy BEFORE ranking → pure ranker over survivors with no catalog access (type-signature-enforced, ADR-008 ScoreProvider port) → selection or first-class NO_ACTION with denial codes; full candidate trace.
path_prefixes: packages/modules/src/decision/
key_files: application/gate.ts (PolicyGate evaluate(), CHECK_ORDER 1..7: consent, suppression, quietHours, frequency, eligibility, inventory, campaignConflict; denials accumulate, unevaluable check fails closed immediately), application/decide.ts, rank.ts, weights.ts, trace.ts, scores.ts; domain/codes.ts (POLICY_VERSION, DenialCode); http/routes.ts
entrypoints: decisionRoutes (/v1/decisions, /batch ≤500, /{id}, /summary, /policy/evaluate simulator, /decision-codes, /decision-weights)
responsibilities: gate split customer-half (once/decision) + offer-half (once/candidate) — evaluation strategy, same functions; deterministic given inputs+policy version.
invariants: ranker cannot reach catalog; SCORE_UNAVAILABLE declared rather than substituting zero; trace stores whole candidate set (reproducibility unit = the trace).
pitfalls: normalised margin is the one set-relative term; capacity reservation must be conditional UPDATE not lock.
confidence: verified

## Files (10+)

- `packages/modules/src/decision/application/decide.ts`
- `packages/modules/src/decision/application/gate.ts`
- `packages/modules/src/decision/application/scores.ts`
- `packages/modules/src/decision/application/trace.ts`
- `packages/modules/src/decision/application/weights.ts`
- `packages/modules/src/decision/domain/codes.ts`
- `packages/modules/src/decision/domain/rank.ts`
- `packages/modules/src/decision/http/routes.ts`
- `packages/modules/src/decision/index.ts`
- `packages/modules/src/decision/jobs.ts`

## API surface

- `POST /decision-weights`
- `GET /decision-weights`
- `POST /policy/evaluate`
- `POST /decisions/:id/outcome`
- `GET /decisions/:id`
- `GET /decisions/summary`
- `GET /decisions`
- `POST /decisions/batch`
- `POST /decisions`
- `GET /decision-codes`
