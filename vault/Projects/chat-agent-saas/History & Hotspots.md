---
cortex-generated: true
title: chat-agent-saas history
tags: [history/project]
---

# chat-agent-saas — History & Hotspots

467 mined commits.

## Commit mix

| Category | Count |
|---|---|
| feat | 190 |
| fix | 117 |
| chore | 112 |
| docs | 24 |
| refactor | 24 |

## Hotspots (most-changed files — treat changes here carefully)

- `packages/web/src/i18n/locales/ar.ts` — touched 76×
- `packages/web/src/i18n/locales/en.ts` — touched 75×
- `packages/api/src/modules/chat/chat.service.ts` — touched 49×
- `packages/api/prisma/schema.prisma` — touched 38×
- `packages/widget/src/core/ChatWidget.ts` — touched 33×
- `packages/api/src/app.ts` — touched 30×
- `package-lock.json` — touched 27×
- `packages/api/src/services/odoo/odooTools.ts` — touched 24×
- `packages/web/src/components/layout/DashboardLayout.tsx` — touched 23×
- `packages/api/package.json` — touched 22×
- `packages/api/src/index.ts` — touched 22×
- `packages/web/src/pages/IntegrationsPage.tsx` — touched 20×
- `packages/platform-admin/src/pages/OrgDetailPage.tsx` — touched 19×
- `packages/web/src/pages/EmbedPage.tsx` — touched 19×
- `packages/api/src/modules/chat/widget.routes.ts` — touched 17×
- `packages/api/src/services/odoo/odooTools.test.ts` — touched 17×
- `packages/web/src/App.tsx` — touched 16×
- `packages/api/src/modules/agents/agent.service.ts` — touched 14×
- `packages/api/src/modules/odoo/odoo.service.ts` — touched 14×
- `packages/api/src/services/dynatrace/dynatraceTools.ts` — touched 14×

## Recent fixes (past pitfalls live here)

- `008eb0503d` 2026-08-07 fix(odoo-addon): Odoo 19 compatibility — nonce replay guard silently no-oped, test fixtures used removed field
- `5fc560eed0` 2026-08-07 fix(api): CRITICAL — policy.manifest.json never made it into dist/, breaking every Odoo tool call in productio
- `e5d1609c3d` 2026-08-07 fix(odoo): 3 real defects found by running the addon against a live Odoo 18
- `f5ede8aee8` 2026-08-07 fix(odoo): wire deny-by-default policy enforcement into service AND end_user mode (GAP-2, D-1, D-2)
- `2b3bc43b11` 2026-08-06 fix(odoo-addon): name exactly which Botify config field is missing
- `831dade53a` 2026-08-06 fix(odoo): correctness/safety hardening for the agent tool layer
- `0a3aba1d61` 2026-08-04 fix(chat): log stream-request failures — currently invisible server-side
- `0ed64f5f3a` 2026-08-04 fix(chat): the streaming crash guard didn't cover the actual crash site
- `1694f0d542` 2026-08-04 fix(chat): guarantee a real answer when the tool loop hits its iteration cap
- `34b4459cf1` 2026-08-04 fix(api): NotFoundError doubled "not found" in every 404 message platform-wide
- `437458c671` 2026-08-04 fix(chat): fall back to non-streaming invoke when a stream crashes before any chunk
- `83e0b23e1d` 2026-08-04 fix(odoo): discovery scan was invisible to real custom modules
- `a25053ad64` 2026-08-04 fix(files): hard-gate file generation on explicit user intent
- `a6db82ae1a` 2026-08-04 fix(odoo): official-author check missed bare "Odoo"/"odoo" spellings
- `c2bb5fb8a7` 2026-08-04 fix(chat): recover from a mid-stream @langchain/google-genai crash on tool calls
- `d62ff51613` 2026-08-04 fix(widget): stream errors were silently swallowed — the "hangs" bug
- `f4832d983c` 2026-08-04 fix(odoo-addon): res.users.groups_id removed in Odoo 19
- `30d60b63be` 2026-08-03 fix(odoo): expose end-user identity mode in the connection UI
- `6c50e54b4b` 2026-07-31 fix(web): bind language to the URL — one switcher, one source of truth
- `b0fc63b3fd` 2026-07-27 fix(ai): sanitize tool schemas for Gemini; prod ops hardening
