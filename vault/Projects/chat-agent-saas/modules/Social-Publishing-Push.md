---
cortex-generated: true
title: social-publishing-push
tags: [module]
---

# social publishing & push

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- SocialAccount/SocialPost/SocialPostTarget for organic publishing to FB Page/IG/LinkedIn/X via OAuth'd connections; repeatable scan promotes due posts, metrics sweep every 6h (`queue.ts:83-93`, `social.worker.ts`).
- Push: PushSubscriber (web/FCM/APNs, endpointHash uniqueness) + PushDelivery per device; public collector endpoints any-origin (`app.ts:179-185`); VAPID/service-account creds reuse IntegrationConnection plumbing (schema comment 1793-1797).

