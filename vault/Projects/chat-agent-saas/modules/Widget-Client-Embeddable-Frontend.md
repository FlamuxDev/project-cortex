---
cortex-generated: true
title: widget-client-embeddable-frontend
tags: [module]
---

# widget client (embeddable frontend)

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Paths: `packages/widget/src/{main.ts,core/*,voice-entry.ts}`; built as a framework-free IIFE via Vite (`vite.config.ts`) with a separate voice bundle (`vite.voice.config.ts`).
- Entry: the embed `<script data-agent-id data-api-url>` mounts `ChatWidget` into a Shadow DOM root (style isolation), exposes `window.Shamsi` and replays pending `postMessage` preview overrides (`main.ts:3-15`). Config (colors/texts/locale/compliance banner/voice flags) comes from `GET /api/widget/:agentId` which whitelists and clamps every field server-side — hex colors regex-checked, strings length-capped, URLs protocol-validated before reaching the client (`widget.routes.ts:31-120`).
- Chat transport: SSE `/stream` with fallback to POST `/message`; markdown rendering sanitized locally (`core/widget-markdown.ts`, markup builder `widget-message-markup.ts`); conversation resume via localStorage + identity token header when verified.
- Voice: ElevenLabs WebRTC via signed-url/conversational-token endpoints; transcript imported to the platform conversation on /stop (`services/elevenlabs/voiceTranscript.ts`), voice-minute quota checked server-side (`assertVoiceQuota`).

