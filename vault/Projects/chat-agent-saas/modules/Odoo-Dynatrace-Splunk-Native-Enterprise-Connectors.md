---
cortex-generated: true
title: odoo-dynatrace-splunk-native-enterprise-connectors
tags: [module]
---

# odoo / dynatrace / splunk (native enterprise connectors)

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Odoo: org-level `OdooConnection` (JSON-2/jsonrpc auto-detect, discovered env snapshot, addon HMAC secret with rotation grace window, identityMode service|end_user) + per-agent `AgentOdooConnection` with deny-by-default op classes (read always-on; capture/normal/financial/lifecycle/batch writes individually granted; accessMode internal_only default) (`schema.prisma:760-878`). Writes flow through a durable ledger `OdooOperation` with idempotencyKey, payloadHash re-check on approval, state machine pending→approved→executed/reconciled (`schema.prisma:886-948`, `services/odoo/operationLedger.ts`, executor + worker `odooOperations.worker.ts`); dedicated minimal audit trail `OdooAuditEvent` (955-986). Docs: `docs/odoo/{architecture,policy,migration,threat-model}.md`.
- End-user execution: in `identityMode:'end_user'` the Botify Odoo addon executes tool calls via `with_user()` so *Odoo's own* ACLs/record-rules/company scoping decide outcomes; reads degrade to fields the acting user may see (commit 38d0d34); the per-session delegation key proves possession for per-operation grants (`services/odoo/grant.ts`, `endUserExecution.test.ts`, `odooAddonClient.ts`). Tenant model policy overlay lets operators classify their own custom/Studio models that the hash-pinned global manifest cannot know (`policy/tenantModels.ts`, schema comment 784-796).
- Shared capability framework: `capabilityRegistry.ts` (per-provider feature detection), `accessPolicy.ts` (who may see which tools given accessMode + identity), `evidence.ts` (structured extraction of results for ReportArtifacts), `evaluationSuites.ts` — introduced by the "integrations: shared capability/policy/evidence framework" commit e295587 and adopted by odoo/dynatrace/splunk commits cdab0c1/3489105/8d76b83.
- Dynatrace: read-only Env API v2 tools + Grail DQL via optional Platform token; per-agent allowedTools/defaultScope and opt-in workflow allowlist double-checked at call time (`schema.prisma:992-1059`, services/dynatrace/*). Hard-won lessons encoded as fixes: classic Events API retirement fallback to DQL (113d3d0), forecast execute-path pulled then re-landed on the real Davis Analyzers path (0b231ea→400b9bd), scope-aware gating with self-healing stale-scope windows (323168a).
- Splunk: read-only SOC triage mirroring dynatrace; SPL free-form is re-enforced against `allowedIndexes` at call time, backtick-bypass and cross-connection circuit collisions patched (1061b33) (`schema.prisma:1064-1110`).
- All three share the capability/evidence/access-policy framework in `services/integrations/{capabilityRegistry,accessPolicy,evidence}.ts` and expose `accessMode` publication boundary (origin never authentication — comment at schema.prisma:1098).

