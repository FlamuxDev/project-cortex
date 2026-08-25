---
cortex-generated: true
title: chat-agent-saas tests
tags: [tests/project]
---

# chat-agent-saas — Test Map

161 test files.

| Kind | Count |
|---|---|
| integration | 40 |
| unit | 121 |

## integration (40)

- `integrations/odoo/botify_agent/tests/__init__.py`
- `integrations/odoo/botify_agent/tests/_helpers.py`
- `integrations/odoo/botify_agent/tests/test_delegation_and_nonce.py`
- `integrations/odoo/botify_agent/tests/test_grant_and_rpc.py`
- `integrations/odoo/botify_agent/tests/test_identity.py`
- `integrations/odoo/botify_agent/tests/test_pure_canonical.py`
- `integrations/odoo/botify_agent/tests/test_pure_grant_security.py`
- `integrations/odoo/botify_agent/tests/test_pure_policy.py`
- `integrations/odoo/botify_agent/tests/test_rpc_permissions.py`
- `packages/api/src/modules/integrations/catalog.service.test.ts` — covers 1 targets
- `packages/api/src/modules/integrations/webhook.legacy.e2e.test.ts` — covers 2 targets
- `packages/api/src/services/integrations/accessPolicy.test.ts` — covers 1 targets
- `packages/api/src/services/integrations/capabilityRegistry.test.ts` — covers 1 targets
- `packages/api/src/services/integrations/core/__probe.test.ts` — covers 2 targets
- `packages/api/src/services/integrations/core/__smoke__/phase1.e2e.test.ts` — covers 5 targets
- `packages/api/src/services/integrations/core/byoa.e2e.test.ts` — covers 2 targets
- `packages/api/src/services/integrations/core/email-message.test.ts` — covers 1 targets
- `packages/api/src/services/integrations/core/meta-oauth.test.ts` — covers 1 targets
- `packages/api/src/services/integrations/core/oauth-state.e2e.test.ts` — covers 2 targets
- `packages/api/src/services/integrations/core/outbound-dispatcher.test.ts` — covers 3 targets
- `packages/api/src/services/integrations/core/provider-registry.flags.test.ts` — covers 2 targets
- `packages/api/src/services/integrations/core/provider-registry.test.ts` — covers 2 targets
- `packages/api/src/services/integrations/core/rate-limiter.test.ts` — covers 1 targets
- `packages/api/src/services/integrations/core/signature.test.ts` — covers 1 targets
- `packages/api/src/services/integrations/core/token-vault.e2e.test.ts` — covers 2 targets
- `packages/api/src/services/integrations/evaluationSuites.test.ts` — covers 2 targets
- `packages/api/src/services/integrations/providers/email-bridge.provider.test.ts` — covers 2 targets
- `packages/api/src/services/integrations/providers/facebook-messenger.provider.test.ts` — covers 1 targets
- `packages/api/src/services/integrations/providers/gmail.provider.test.ts` — covers 1 targets
- `packages/api/src/services/integrations/providers/instagram-dm.provider.test.ts` — covers 1 targets
- `packages/api/src/services/integrations/providers/linkedin-leads.provider.test.ts` — covers 1 targets
- `packages/api/src/services/integrations/providers/microsoft-teams.provider.test.ts` — covers 2 targets
- `packages/api/src/services/integrations/providers/outlook.provider.test.ts` — covers 1 targets
- `packages/api/src/services/integrations/providers/slack.provider.test.ts` — covers 2 targets
- `packages/api/src/services/integrations/providers/sms.provider.test.ts` — covers 2 targets
- `packages/api/src/services/integrations/providers/telegram.provider.test.ts` — covers 1 targets
- `packages/api/src/services/integrations/providers/webhook.provider.test.ts` — covers 2 targets
- `packages/api/src/services/integrations/providers/whatsapp.provider.test.ts` — covers 3 targets
- `packages/api/src/services/integrations/providers/x.provider.test.ts` — covers 1 targets
- `packages/api/src/services/integrations/timeframe.test.ts` — covers 1 targets

## unit (121)

- `packages/api/src/__e2e__/tenant-isolation.e2e.test.ts` — covers 3 targets
- `packages/api/src/jobs/workers/auditRetention.test.ts` — covers 1 targets
- `packages/api/src/jobs/workers/knowledge.worker.test.ts` — covers 1 targets
- `packages/api/src/jobs/workers/odooOperations.worker.test.ts` — covers 1 targets
- `packages/api/src/jobs/workers/retention.parse.test.ts` — covers 1 targets
- `packages/api/src/middleware/authRoleExpiry.test.ts` — covers 1 targets
- `packages/api/src/modules/agents/agent-config.compliance.test.ts` — covers 1 targets
- `packages/api/src/modules/agents/agent-origin.service.test.ts` — covers 1 targets
- `packages/api/src/modules/analytics/analytics.report.export.test.ts` — covers 2 targets
- `packages/api/src/modules/artifacts/artifact.routes.test.ts` — covers 1 targets
- `packages/api/src/modules/auth/auth.schemas.test.ts` — covers 1 targets
- `packages/api/src/modules/chat/chat.controller.streamError.test.ts` — covers 2 targets
- `packages/api/src/modules/chat/chat.service.screening.test.ts` — covers 1 targets
- `packages/api/src/modules/chat/conversation-ownership.test.ts` — covers 1 targets
- `packages/api/src/modules/chat/invokeToolWithTimeout.test.ts` — covers 1 targets
- `packages/api/src/modules/chat/pruneToolMessages.test.ts` — covers 1 targets
- `packages/api/src/modules/chat/runToolLoop.llmTimeout.test.ts` — covers 1 targets
- `packages/api/src/modules/chat/runToolLoop.usage.test.ts` — covers 1 targets
- `packages/api/src/modules/chat/streamMarkerFilter.test.ts` — covers 1 targets
- `packages/api/src/modules/dynatrace/dynatrace.service.ssrf.test.ts` — covers 1 targets
- `packages/api/src/modules/knowledge/suggestions.service.test.ts` — covers 1 targets
- `packages/api/src/modules/odoo/odoo.operations.test.ts` — covers 4 targets
- `packages/api/src/modules/odoo/odoo.secretRotation.test.ts` — covers 1 targets
- `packages/api/src/modules/odoo/odoo.service.ssrf.test.ts` — covers 1 targets
- `packages/api/src/modules/organizations/org.routes.test.ts`
- `packages/api/src/modules/outreach/segment.service.test.ts` — covers 2 targets
- `packages/api/src/modules/platform/orgAudit.test.ts` — covers 1 targets
- `packages/api/src/openapi.test.ts` — covers 1 targets
- `packages/api/src/services/ai/actingUserPrompt.test.ts` — covers 1 targets
- `packages/api/src/services/ai/customActions.test.ts` — covers 1 targets
- `packages/api/src/services/ai/fileTools.test.ts` — covers 4 targets
- `packages/api/src/services/ai/geminiToolSchema.test.ts` — covers 1 targets
- `packages/api/src/services/ai/marketing/contentWriter.test.ts` — covers 1 targets
- `packages/api/src/services/ai/memory.test.ts` — covers 1 targets
- `packages/api/src/services/ai/modelProvider.test.ts` — covers 1 targets
- `packages/api/src/services/ai/personalityPrompt.compliance.test.ts` — covers 1 targets
- `packages/api/src/services/ai/personalityPrompt.test.ts` — covers 1 targets
- `packages/api/src/services/ai/rag.injection.test.ts` — covers 1 targets
- `packages/api/src/services/ai/safetyScreening.test.ts` — covers 1 targets
- `packages/api/src/services/alerts/alertLock.test.ts` — covers 1 targets
- `packages/api/src/services/alerts/alertMetrics.test.ts` — covers 2 targets
- `packages/api/src/services/alerts/alertRules.test.ts` — covers 1 targets
- `packages/api/src/services/dynatrace/agentTools.test.ts` — covers 1 targets
- `packages/api/src/services/dynatrace/dynatraceClient.test.ts` — covers 4 targets
- `packages/api/src/services/dynatrace/dynatraceDiscovery.test.ts` — covers 1 targets
- `packages/api/src/services/dynatrace/dynatraceErrors.test.ts` — covers 2 targets
- `packages/api/src/services/dynatrace/dynatraceFormat.test.ts` — covers 2 targets
- `packages/api/src/services/dynatrace/dynatraceGrail.test.ts` — covers 5 targets
- `packages/api/src/services/dynatrace/dynatraceTools.classicMetricsHint.test.ts` — covers 4 targets
- `packages/api/src/services/dynatrace/dynatraceTools.eventsGrailFallback.test.ts` — covers 4 targets
- …and 71 more

## High-importance code with no obvious mapped test

_Heuristic (name/import match). Verify before treating as gaps._

- `packages/api/src/modules/platform/platform.routes.ts`
- `packages/api/src/utils/logger.ts`
- `packages/api/src/modules/outreach/outreach.routes.ts`
- `packages/api/src/modules/odoo/odoo.routes.ts`
- `packages/api/src/modules/agents/agent.routes.ts`
- `packages/api/src/modules/chat/chat.routes.ts`
- `packages/api/src/modules/auth/auth.routes.ts`
- `packages/api/src/modules/knowledge/knowledge.routes.ts`
- `packages/platform-admin/src/stores/i18nStore.ts`
- `packages/api/src/modules/dynatrace/dynatrace.routes.ts`
- `packages/api/src/modules/mcp/mcp.routes.ts`
- `packages/api/src/modules/splunk/splunk.routes.ts`
- `packages/api/src/modules/analytics/analytics.routes.ts`
- `packages/api/src/middleware/validate.ts`
- `packages/api/src/modules/integrations/oauth.routes.ts`
- `packages/api/src/modules/outreach/journey.routes.ts`
- `packages/web/src/services/integrationsV2.ts`
- `packages/api/src/modules/organizations/org.routes.ts`
- `packages/api/src/modules/outreach/segment.routes.ts`
- `packages/api/src/modules/social/social.routes.ts`
- `packages/web/src/screens/OutreachPage.tsx`
- `packages/api/src/middleware/orgFeature.ts`
- `packages/api/src/modules/ai-studio/ai.routes.ts`
- `packages/api/src/modules/push/push.routes.ts`
- `packages/api/src/modules/integrations/webhook.routes.ts`
