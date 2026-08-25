---
cortex-generated: true
title: campaign-domain-state-machine-audience-approval
tags: [module]
---

# campaign domain, state machine, audience, approval

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `packages/core/src/campaigns`

purpose: lifecycle draft→in_review→scheduled→running… with version-bound four-eyes approval.
path_prefixes: packages/core/src/campaigns
key_files: packages/core/src/campaigns/state.ts, approval.ts, blockers.ts, configuration.ts, fingerprint.ts, objectives.ts, repository.ts
entrypoints: /v1/workspaces/:id/campaigns* (***REDACTED-B64***)
responsibilities: explicit transition table transcribing PRD §7.2; approval certifies audience under repeatable read and freezes the active version; blockers computed for the UI.
invariants: engine transitions (`start`,`complete`,`fail`…) are UNREACHABLE over HTTP — actor defaults to 'api' so forgetting to say who is acting cannot start execution (state.ts:220); submitter cannot approve (four-eyes; no owner exemption until M18 made a members UI exist — PROGRESS.md); failed is recoverable via `fix`→draft, terminal statuses are completed/stopped only; edit allowed only in draft; scheduled/running/paused versions frozen.
pitfalls: a GENERIC transition route once could approve a campaign (commit fac3d6d) — transition-specific routes exist since; stop exists only from paused (deliberate two-step destructive action).
confidence: verified

## Files (10+)

- `packages/core/src/campaigns/approval.ts`
- `packages/core/src/campaigns/blockers.ts`
- `packages/core/src/campaigns/configuration.ts`
- `packages/core/src/campaigns/fingerprint.ts`
- `packages/core/src/campaigns/objectives.ts`
- `packages/core/src/campaigns/objectives.unit.test.ts`
- `packages/core/src/campaigns/repository.ts`
- `packages/core/src/campaigns/state.ts`
- `packages/core/src/campaigns/state.unit.test.ts`
- `packages/core/src/campaigns/types.ts`
