---
cortex-generated: true
title: campify history
tags: [history/project]
---

# Campify — History & Hotspots

109 mined commits.

## Commit mix

| Category | Count |
|---|---|
| feat | 51 |
| fix | 26 |
| chore | 17 |
| docs | 15 |

## Hotspots (most-changed files — treat changes here carefully)

- `docs/engineering/PROGRESS.md` — touched 40×
- `apps/api/src/app.ts` — touched 34×
- `apps/web/src/lib/i18n.ts` — touched 20×
- `packages/core/src/index.ts` — touched 20×
- `docs/engineering/REQUIREMENTS_TRACEABILITY.md` — touched 19×
- `e2e/campaign.spec.ts` — touched 17×
- `apps/web/src/components/Shell.tsx` — touched 14×
- `packages/core/src/audit/index.ts` — touched 14×
- `packages/core/src/identity/service.ts` — touched 14×
- `packages/db/test/all-tables.tenancy.test.ts` — touched 13×
- `apps/web/src/lib/actions.ts` — touched 12×
- `apps/api/test/authz.contract.test.ts` — touched 11×
- `apps/api/test/campaigns.contract.test.ts` — touched 11×
- `pnpm-lock.yaml` — touched 11×
- `apps/api/src/server.ts` — touched 10×
- `apps/web/src/app/globals.css` — touched 10×
- `packages/core/src/imports/commit.ts` — touched 10×
- `apps/api/src/campaignRoutes.ts` — touched 9×
- `docs/engineering/DELIVERY_PLAN.md` — touched 9×
- `packages/core/src/contacts/repository.ts` — touched 9×

## Recent fixes (past pitfalls live here)

- `fac3d6d5e9` 2026-08-09 fix(campaigns): the generic transition route could approve a campaign [FR-CAM-005][SEC-003]
- `1d0f49c3ef` 2026-08-08 fix(security): close every finding from the pre-launch review [FR-ADM-003][SEC-001] (#24)
- `a38a0c8004` 2026-08-08 fix: post-launch production remediation [FR-AUTH-001][FR-AUTH-003][SEC-001][SEC-003][SEC-007] (#27)
- `bfa577e5d6` 2026-08-08 fix(ops): make the migration runner and the API bind deployable [ADR-0003][ADR-0011] (#25)
- `157d8bddb9` 2026-08-07 fix(webhooks): defects the M4B follow-on independent review found [FR-INT-005][FR-INT-006]
- `5c798759dc` 2026-08-07 fix(web): audience tab shows translated blocker text, not raw codes [FR-CAM-003] (#10)
- `bcc0da6161` 2026-08-07 fix(dev): propagate API_URL to the web process when API_PORT is overridden (#13)
- `cf88b83c96` 2026-08-07 fix(analytics): anchor attribution on messages.sent_at, and fix the queue-suite flake [FR-ANL-002][NFR-REL-002
- `1222aa2aa4` 2026-08-06 fix(analytics): defects the M4A independent review found [FR-ANL-002][FR-ANL-003][FR-ANL-004][FR-ANL-005][FR-I
- `24d8656a91` 2026-08-06 fix(sales): defects the M4B independent review found [FR-SAL-001][FR-SAL-002][FR-SAL-003][FR-SAL-004]
- `bb12ce6101` 2026-08-06 fix(security): defects the M3B independent review found [FR-JRN-002][FR-JRN-006][FR-JRN-007][FR-JRN-008][FR-CA
- `063c501370` 2026-08-01 fix: quadratic XLSX parsing, per-entry inflation cap, bypassable body guard
- `12ef360212` 2026-08-01 fix(security): defects the last two reviews found in the last two reviews' fixes
- `1cdde20035` 2026-08-01 fix: refundable cell budget, unnormalised suppression, self-deleting timeouts
- `1e1b32d8ed` 2026-08-01 fix: recount required only segments:read, and the web gate was presence-only
- `40e66ad911` 2026-08-01 fix(availability): bound total cells, batch commit, cap query time
- `9e536ddcca` 2026-08-01 fix(security): login CSRF, throttle collapse, and unbounded segment reads
- `9f851611cb` 2026-08-01 fix(security): trustProxy made the rate limit decoration and a lockout weapon
- `e9d50e0eac` 2026-08-01 fix(security): a confused deputy, a shared rate-limit bucket, and a PRD I misread
- `fb73083fd6` 2026-08-01 fix: audit every lazy quantifier, bound inflation cumulatively, backfill via domain
