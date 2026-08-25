---
cortex-generated: true
title: cvm history
tags: [history/project]
---

# CVM — History & Hotspots

91 mined commits.

## Commit mix

| Category | Count |
|---|---|
| feat | 54 |
| fix | 20 |
| chore | 9 |
| docs | 8 |

## Hotspots (most-changed files — treat changes here carefully)

- `apps/web/src/lib/dictionaries/ar.ts` — touched 20×
- `e2e/golden-path.spec.ts` — touched 18×
- `apps/web/src/app/(app)/customers/[id]/page.tsx` — touched 17×
- `docs/api/openapi.json` — touched 17×
- `apps/web/src/components/ui.tsx` — touched 15×
- `apps/web/src/lib/api-types.ts` — touched 15×
- `packages/modules/src/audit/domain/types.ts` — touched 15×
- `apps/api/src/app.ts` — touched 14×
- `apps/web/src/lib/nav.ts` — touched 14×
- `package.json` — touched 14×
- `apps/web/src/app/(app)/customers/page.tsx` — touched 13×
- `apps/web/src/lib/api.ts` — touched 13×
- `packages/platform/__tests__/tenant-isolation.int.test.ts` — touched 13×
- `apps/web/src/app/(app)/layout.tsx` — touched 12×
- `apps/web/src/app/(app)/page.tsx` — touched 12×
- `apps/worker/src/main.ts` — touched 12×
- `packages/platform/src/db/schema/index.ts` — touched 12×
- `apps/web/src/app/(app)/administration/page.tsx` — touched 11×
- `apps/web/src/app/(app)/identity/page.tsx` — touched 11×
- `packages/modules/src/tenancy/domain/roles.ts` — touched 11×

## Recent fixes (past pitfalls live here)

- `55d8c35b56` 2026-08-19 fix(profile): the timeline's category filter answered 500, then answered nothing
- `594c702614` 2026-08-19 fix(features): the highest-scoring customer was labelled `low`
- `5d9b45ac28` 2026-08-19 fix(web): restore the operational page titles, keep the numbering
- `660bb4877e` 2026-08-19 fix(web): the gate could not see the strings that shipped in English
- `802f6c5c08` 2026-08-19 fix(profile): a file load about somebody is not that person doing something
- `b05dfb72c0` 2026-08-19 fix(web): sign-in inherits the design system instead of hand-rolling it
- `bd920f1691` 2026-08-19 fix(web): "Models (0)" was false — there are eight, and all of them are fine
- `ef6ca9a898` 2026-08-19 fix(ci): start the scheduler, without which the golden path cannot pass
- `0283a399ac` 2026-08-17 fix(web): revert the CSP change — it was load-bearing, and e2e caught it
- `03d1d04bda` 2026-08-17 fix(web): a duplicate React key was dropping identity link history
- `0f58daf791` 2026-08-17 fix: three defects the game day found, and the signal scenario 1 needed
- `2f35b9b79f` 2026-08-17 fix: three more defects, found by rolling back and by starting from empty
- `48cfc42e33` 2026-08-17 fix(web): the CSP broke every form in the product, and self-host the fonts
- `5eafe7ff67` 2026-08-17 fix: the processing register had no writers
- `a7907e9608` 2026-08-17 fix: two runners on one ingestion batch double its counters
- `df4137cd64` 2026-08-17 fix: three more caught unique violations, and close out Phase 6
- `0012387c48` 2026-08-16 fix: the web image has never built
- `f47a6ef671` 2026-08-16 fix: close every open item in Phase 2, and twelve defects found doing it
- `f4d6a2f5d1` 2026-08-16 fix: recurring jobs were dead-lettering on every firing
- `8fe2f6113a` 2026-08-15 fix: telemetry produced zero spans under ESM; correct the completion record
