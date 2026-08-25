---
cortex-generated: true
title: chat-conversation-engine
tags: [module]
---

# chat / conversation engine

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- `modules/chat/chat.routes.ts`: public widget surface (message, stream, close, handoff, widget-messages, rating, export, upload-attachment) each gated by `assertAgentOriginAllowed` + zod body validation + `requireConversationAccess` ownership middleware (routes :79-146); dashboard half switches to `authenticate` mid-router (:149-187) — which is why `identityRoutes` must mount before `chatRoutes` (`app.ts:297-300`).
- `resolveConversationId` (`chat.service.ts:1015-1121`): resume-by-(agent, channel, sender-or-identity), closed→new thread, anonymous→verified **adoption** which permanently closes the thread to anonymous callers (comment at 1100-1110).
- Ownership check returns NotFound (not Forbidden) to avoid existence oracle (`assertConversationOwnership`, 1123-1140).
- Handoff: `requestHumanHandoff` stamps `humanHandoffAt`; while open, AI stays silent (`processMessage` early-return 1521-1529); support staff reply as role `human` from the inbox (`modules/support/support.service.ts:75-100`) and forwards to the originating channel via `integration-messaging.service`.

