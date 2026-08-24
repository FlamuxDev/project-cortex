---
cortex-generated: true
title: the-gemini-agent
tags: [module]
---

# The Gemini agent

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `packages/ai/src/application/ai-agent/`

purpose: system prompt + tool-calling loop + the single server integrity invariant.
path_prefixes: packages/ai/src/application/ai-agent/
key_files: agent.ts (`buildMessages` 6-rule history normalization — final turn always user; `runWhatsAppAgent` generateText toolChoice auto stopWhen stepCountIs(8); integrity retry once with INTEGRITY_NUDGE then drop text; `fallbackReply`), guard.ts (`collectToolOutcomes`/`checkIntegrity` AR+EN claim regexes — see §B.1 in CLAUDE.md, the SOLE written spec), confidential.ts (`sanitizeToolOutput` strips secret-shaped keys/values, fail-open on shape, never strips appointment_id/scheduled_at), context.ts (`loadAgentContext`: history+services+RAG+profile+scheduling), preview.ts (`runAgentPreview`, dryRun:true tools :144), tools/ (names.ts AGENT_TOOL_NAMES: get_business_snapshot, list_customer_appointments, search_availability, book_appointment, confirm_appointment, cancel_appointment, reschedule_appointment, quote_price)
entrypoints: whatsapp-inbound orchestrator; /api/dashboard/ai/preview
invariants: §B.1 contract — never feed raw ctx.history to generateText; thinking disabled (`AGENT_MODEL_SETTINGS` temperature 0, maxOutputTokens 2048, thinkingBudget 0 in infrastructure/ai/gemini.ts); model decides every tool call (no keyword routing, no reply re-authoring — deleted regex layers must not return)
pitfalls: two independent causes of "Gemini 200 + empty candidates": malformed history AND thinking eating token budget; both caused the same prod outage once
confidence: high

## Files (15+)

- `packages/ai/src/application/ai-agent/agent.test.ts`
- `packages/ai/src/application/ai-agent/agent.ts`
- `packages/ai/src/application/ai-agent/confidential.test.ts`
- `packages/ai/src/application/ai-agent/confidential.ts`
- `packages/ai/src/application/ai-agent/context.ts`
- `packages/ai/src/application/ai-agent/guard.test.ts`
- `packages/ai/src/application/ai-agent/guard.ts`
- `packages/ai/src/application/ai-agent/preview.ts`
- `packages/ai/src/application/ai-agent/tools/agent-tools.test.ts`
- `packages/ai/src/application/ai-agent/tools/appointments.ts`
- `packages/ai/src/application/ai-agent/tools/catalog.ts`
- `packages/ai/src/application/ai-agent/tools/index.ts`
- `packages/ai/src/application/ai-agent/tools/names.ts`
- `packages/ai/src/application/ai-agent/tools/slot-query.ts`
- `packages/ai/src/application/ai-agent/tools/types.ts`
