---
cortex-generated: true
title: safety-screening-layer
tags: [module]
---

# safety screening layer

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- `services/ai/safetyScreening.ts`: `computeScreening` (chat.service.ts:1348) classifies the user turn via LLM when org config enables it; `applySafetyScreening` (1404) acts on verdicts — `containment` returns transcript-only response, `handoff` triggers human escalation, `flag`/`none` fall through. Deliberately invoked *inside* processMessage/processMessageStream so every entry point (widget, webhook, voice, playground) gets it, not just two routes (comment at chat.routes.ts:75-78).
- Custom HTTP actions are risk-tiered behind a deterministic confirmation gate: high-risk actions require an explicit approval reply intercepted before the LLM runs (`resolveActionConfirmationFromReply` at chat.service.ts:1557-1568, `services/ai/customActions.ts`, "risk-tier custom actions behind a confirmation gate" commit 129ea16). Every resolved action URL passes the SSRF guard at call time (schema comment 383-388, `services/security/urlGuard.ts`).

