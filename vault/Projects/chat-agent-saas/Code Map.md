---
cortex-generated: true
title: chat-agent-saas code map
tags: [codemap/project]
---

# chat-agent-saas — Code Map

## Directory layout (indexed files)

- `packages/` — 924 files
- `integrations/` — 23 files
- `scripts/` — 4 files
- `ecosystem.config.cjs/` — 1 files
- `eslint.config.js/` — 1 files
- `fix_widget.js/` — 1 files
- `patch_widget.js/` — 1 files
- `patch_widget2.js/` — 1 files
- `test_chat.ts/` — 1 files

## Entry points

- `packages/api/src/app.ts`
- `packages/web/src/components/integrations/index.ts`
- `packages/api/src/services/integrations/providers/index.ts`
- `packages/web/src/app/llms.txt/route.ts`
- `packages/shared/src/constants/index.ts`
- `packages/shared/src/index.ts`
- `packages/shared/src/types/index.ts`
- `packages/web/src/i18n/index.ts`
- `packages/platform-admin/src/app/(console)/admins/page.tsx`
- `packages/platform-admin/src/app/(console)/ai-models/page.tsx`
- `packages/platform-admin/src/app/(console)/audit-log/page.tsx`
- `packages/platform-admin/src/app/(console)/billing/orgs/[orgId]/page.tsx`
- `packages/platform-admin/src/app/(console)/billing/page.tsx`
- `packages/platform-admin/src/app/(console)/demo-bookings/page.tsx`
- `packages/platform-admin/src/app/(console)/features/page.tsx`

## Most-connected symbols (fan-in leaders)

| Symbol | Kind | Location |
|---|---|---|
| `s` | function | `packages/api/src/services/outreach/journey/engine.ts:64` |
| `s` | function | `packages/api/src/services/reports/reportComposer.ts:77` |
| `error` | function | `integrations/odoo/botify_agent/controllers/_shared.py:108` |
| `cn` | function | `packages/platform-admin/src/utils/cn.ts:4` |
| `cn` | function | `packages/web/src/utils/cn.ts:4` |
| `Update` | type | `packages/web/src/components/embed/sections.tsx:31` |
| `object` | function | `packages/api/src/services/reports/conversationEvidence.ts:32` |
| `authorize` | function | `packages/api/src/middleware/auth.ts:102` |
| `validateBody` | function | `packages/api/src/middleware/validate.ts:19` |
| `Segment` | prisma_model | `packages/api/prisma/schema.prisma:1478` |
| `Segment` | interface | `packages/web/src/screens/SegmentsPage.tsx:87` |
| `evaluateSegment` | function | `packages/api/src/services/outreach/segmentDsl.ts:274` |
| `logAudit` | function | `packages/api/src/modules/platform/audit-log.service.ts:23` |
| `encrypt` | function | `packages/api/src/utils/encryption.ts:65` |
| `post` | function | `packages/api/scripts/verify-identity-prod.js:41` |
| `get` | function | `packages/api/src/modules/integrations/connections.controller.ts:7` |
| `getConfigSync` | function | `packages/api/src/utils/config.ts:103` |
| `GET` | function | `packages/web/src/app/llms.txt/route.ts:34` |
| `get` | function | `packages/api/scripts/dynatrace-demo.ts:85` |
| `get` | function | `packages/api/scripts/splunk-demo.ts:86` |
| `get` | function | `packages/api/scripts/verify-identity-prod.js:57` |
| `num` | function | `packages/api/src/services/ai/marketing/performancePredictor.ts:76` |
| `num` | function | `packages/api/src/services/dynatrace/dynatraceFormat.ts:224` |
| `ts` | function | `packages/api/src/services/transcript/transcriptExport.ts:31` |
| `Provider` | type | `packages/web/src/screens/DeliverabilityPage.tsx:35` |
| `buildOdooTools` | function | `packages/api/src/services/odoo/odooTools.ts:2795` |
| `parseApiError` | function | `packages/platform-admin/src/utils/apiError.ts:20` |
| `parseApiError` | function | `packages/web/src/utils/apiError.ts:21` |
| `Connection` | interface | `packages/web/src/services/integrationsV2.ts:21` |
| `connection` | function | `packages/api/src/services/odoo/endUserExecution.test.ts:18` |

## Highest-importance files

- `packages/api/src/modules/platform/platform.routes.ts` (314 loc)
- `packages/api/src/app.ts` (361 loc)
- `packages/api/src/utils/prisma.ts` (22 loc)
- `packages/api/src/utils/logger.ts` (37 loc)
- `packages/api/src/utils/encryption.ts` (100 loc)
- `packages/api/src/modules/outreach/outreach.routes.ts` (226 loc)
- `packages/api/src/utils/errors.ts` (47 loc)
- `packages/api/src/modules/odoo/odoo.routes.ts` (110 loc)
- `packages/api/src/modules/agents/agent.routes.ts` (95 loc)
- `packages/api/src/utils/config.ts` (136 loc)
- `packages/api/src/modules/chat/chat.routes.ts` (188 loc)
- `packages/web/src/services/api.ts` (85 loc)
- `packages/api/src/modules/auth/auth.routes.ts` (48 loc)
- `packages/api/src/modules/knowledge/knowledge.routes.ts` (39 loc)
- `packages/platform-admin/src/stores/i18nStore.ts` (1504 loc)
- `packages/api/src/modules/dynatrace/dynatrace.routes.ts` (70 loc)
- `packages/api/src/modules/mcp/mcp.routes.ts` (62 loc)
- `packages/api/src/modules/splunk/splunk.routes.ts` (70 loc)
- `packages/api/src/services/dynatrace/__mock__/mockDynatraceServer.ts` (516 loc)
- `packages/api/src/services/integrations/core/provider-registry.ts` (41 loc)
- `packages/web/src/utils/cn.ts` (7 loc)
- `packages/api/src/middleware/auth.ts` (187 loc)
- `packages/api/src/utils/redis.ts` (26 loc)
- `packages/api/src/modules/analytics/analytics.routes.ts` (41 loc)
- `packages/api/src/modules/platform/audit-log.service.ts` (124 loc)