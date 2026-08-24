---
cortex-generated: true
title: odoo-dynatrace-splunk-mcp-channel-providers
tags: [module]
---

# Odoo / Dynatrace / Splunk / MCP / channel providers

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** `packages/api/src/modules/{odoo,dynatrace,splunk,mcp,integrations}/,packages/api/src/services/{odoo,dynatrace,splunk,integrations}/`

purpose: native tool adapters + OAuth/connection lifecycle for customer systems; capability discovery; evidence normalization.
path_prefixes: packages/api/src/modules/{odoo,dynatrace,splunk,mcp,integrations}/, packages/api/src/services/{odoo,dynatrace,splunk,integrations}/
key_files: services/odoo/{agentTools,odooDomainTools,operationAccess,odooErrors,odooCapabilities}.ts(+tests), services/dynatrace/{agentTools,dynatraceClient,dynatraceDiscovery,dynatraceGrail,dynatraceErrors,dynatraceFormat,dynatraceCapabilities}.ts(+12 test files, __mock__/mockDynatraceServer.ts), services/integrations/{capabilityRegistry,accessPolicy,evidence,timeframe,evaluationSuites}.ts (untracked), services/integrations/core/ (oauth-state, token-vault e2e tests), services/mcp/
entrypoints: /api/odoo, /api/dynatrace, /api/splunk admin routers; tools loaded into chat loop via loadChatResources; provider registry populated by side-effect import in index.ts/workers-entry.ts.
responsibilities: per-connection credential vault (AES), SSRF guards (security/urlGuard.ts), scope/model-aware tool gating, Grail-DQL fallback for retired classic APIs, tenant isolation + rate limiting per connection, structured error envelopes replacing free-form strings (in flight).
invariants: Odoo writes go through deny-by-default policy.manifest.json + operation classes + actAs choke point; read degradation to acting-user-visible fields (38d0d34); Dynatrace "system error ≠ empty result" (d5c6955); Splunk SPL backtick-bypass guard (1061b33).
pitfalls: dynatrace_forecast was pulled after its execute path proved wrong LIVE (0b231ea) then re-added only after finding the real Davis Analyzers path (400b9bd) — verify execute paths against prod before shipping tools; missing scope warnings can be stale/false (956b22b: slo.read isn't even offered by Dynatrace's own token editor); policy.manifest.json must reach dist/ (5fc560e CRITICAL prod break).
confidence: verified (capabilityRegistry/evidence layer inferred from audit doc + filenames)

## Files (40+)

- `packages/api/scripts/dynatrace-demo.ts`
- `packages/api/scripts/splunk-demo.ts`
- `packages/api/src/modules/dynatrace/dynatrace.controller.ts`
- `packages/api/src/modules/dynatrace/dynatrace.routes.ts`
- `packages/api/src/modules/dynatrace/dynatrace.schemas.ts`
- `packages/api/src/modules/dynatrace/dynatrace.service.ssrf.test.ts`
- `packages/api/src/modules/dynatrace/dynatrace.service.ts`
- `packages/api/src/modules/mcp/mcp.controller.ts`
- `packages/api/src/modules/mcp/mcp.routes.ts`
- `packages/api/src/modules/mcp/mcp.schemas.ts`
- `packages/api/src/modules/mcp/mcp.service.ts`
- `packages/api/src/modules/splunk/splunk.controller.ts`
- `packages/api/src/modules/splunk/splunk.routes.ts`
- `packages/api/src/modules/splunk/splunk.schemas.ts`
- `packages/api/src/modules/splunk/splunk.service.ts`
- `packages/api/src/services/dynatrace/__mock__/mockDynatraceServer.ts`
- `packages/api/src/services/dynatrace/agentTools.test.ts`
- `packages/api/src/services/dynatrace/agentTools.ts`
- `packages/api/src/services/dynatrace/dynatraceCapabilities.ts`
- `packages/api/src/services/dynatrace/dynatraceClient.test.ts`
- `packages/api/src/services/dynatrace/dynatraceClient.ts`
- `packages/api/src/services/dynatrace/dynatraceDiscovery.test.ts`
- `packages/api/src/services/dynatrace/dynatraceDiscovery.ts`
- `packages/api/src/services/dynatrace/dynatraceErrors.test.ts`
- `packages/api/src/services/dynatrace/dynatraceErrors.ts`

## API surface

- `DELETE /agents/:agentId/connections/:attachmentId`
- `PUT /agents/:agentId/connections/:attachmentId`
- `POST /agents/:agentId/connections`
- `GET /agents/:agentId/connections`
- `POST /connections/:id/scan`
- `POST /connections/:id/test`
- `DELETE /connections/:id`
- `PUT /connections/:id`
- `GET /connections/:id`
- `POST /connections`
- `GET /connections`
- `GET conn-1`
- `DELETE /agents/:agentId/servers/:attachmentId`
- `PUT /agents/:agentId/servers/:attachmentId`
- `POST /agents/:agentId/servers`
