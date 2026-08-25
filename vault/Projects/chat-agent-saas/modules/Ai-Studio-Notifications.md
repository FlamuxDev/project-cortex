---
cortex-generated: true
title: ai-studio-notifications
tags: [module]
---

# ai-studio & notifications

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- `/api/ai` (ai-studio): campaign draft generation, content/ad writing, prediction, insights — LLM utilities behind JWT for the marketing suite (`app.ts:349-350` comment, `modules/ai-studio/ai.routes.ts`).
- Notifications: in-app rows created by `services/notifications` (quota alerts deduped via Redis keys `quota_alert:{org}:{period}:{kind}:{threshold}`, chat.service.ts:899-907), realtime push to user rooms, email fallback; web-push delivery path handled separately by the push module.

