---
cortex-generated: true
title: next-js-ui-bff
tags: [module]
---

# Next.js UI + BFF

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `apps/web/src`

purpose: public site, private app UI, server actions, i18n ar/en RTL.
path_prefixes: apps/web/src
key_files: apps/web/src/middleware.ts, lib/actions.ts, lib/api.ts, lib/i18n.ts, app/(public)/*, app/(app)/*
entrypoints: middleware (session gate + noindex); /api/login,/api/signup proxies; server actions for all mutations
responsibilities: session validated (not shape-checked) per navigation, failing closed; actions carry intent only — rules live in core/API; campaign builder tabs, segment builder, journey canvas, import wizard, team screen.
invariants: /app never indexable (edge header + middleware + robots + automated test, ADR-0009); tokens consumed then redirected away (Next serializes searchParams into RSC payload/history/Referer).
pitfalls: `?next` validated by origin comparison, never regex; waitForURL-before-click race pattern broke tests 3× (PROGRESS.md M15/M18).
confidence: verified

