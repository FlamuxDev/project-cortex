---
cortex-generated: true
title: channels-whatsapp-messaging-integrations
tags: [module]
---

# channels / WhatsApp & messaging integrations

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

Two generations run side by side:
- **Legacy** (`modules/integrations/webhook.routes.ts`, header comment marks it legacy since the 2026-05-24 overhaul): per-agent URLs `/api/webhooks/{telegram|whatsapp|http|email|elevenlabs}/:agentId`. WhatsApp GET does hub.verify_token challenge against per-integration credential or global config fallback (`webhook.routes.ts:513-538`); POST acks 200 immediately, normalizes, gates via `loadActiveIntegration` (integration active + agent active + org active + org features `integrations` and `integration.{platform}`, lines 303-336), marks read, handles `/start`,`/reset`, then calls `processMessage` and sends the reply via Graph API (`sendWhatsAppReply`). Telegram includes voice-note STT/TTS via ElevenLabs.
- **V2** (`webhook-v2.routes.ts` + `services/integrations/core/*` + one file per provider under `providers/`): URL `/api/webhooks/:provider/:channelId`. Flow: early-200 ack → per-channel in-memory rate limit (`core/rate-limiter.ts`) → rawBody signature verification via provider (`whatsapp.provider.ts:132-139` uses Meta `x-hub-signature-256` with app secret) → normalize → `dispatchInbound` (`core/inbound-pipeline.ts:12-89`) which honors inbound STOP/opt-out keywords into the suppression list, resolves media (WhatsApp media id downloaded & re-hosted to S3, `providers/whatsapp.provider.ts:181-199`), then feeds `processMessage` and replies via `outbound-dispatcher`.
- Providers registered by side-effect import of `services/integrations/providers` (`index.ts:39`): whatsapp, telegram, slack, facebook-messenger, instagram-dm, x, linkedin-leads, gmail, outlook, microsoft-teams, sms, email-bridge, webhook, webpush, fcm, apns. A platform-wide Meta webhook (one Meta App across FB/IG/WA) mounts at `/api/integrations/webhook/meta` (`app.ts:325-327`, `webhook-meta.routes.ts`).
- OAuth connections: `IntegrationConnection` (+BYOA client credentials encrypted) with `OAuthState` PKCE rows and a token-refresh queue; token vault e2e-tested (`core/token-vault.e2e.test.ts`, `oauth-state.e2e.test.ts`).

