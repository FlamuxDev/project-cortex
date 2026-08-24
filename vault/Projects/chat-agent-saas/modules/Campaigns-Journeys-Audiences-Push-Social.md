---
cortex-generated: true
title: campaigns-journeys-audiences-push-social
tags: [module]
---

# Campaigns, journeys, audiences, push, social

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** `packages/api/src/modules/outreach/,packages/api/src/services/outreach/,packages/api/src/modules/{social,push}/`

purpose: multi-channel outbound marketing (email/push/social/WhatsApp/SMS lineage), segments, journeys automation, deliverability, consent/suppression.
path_prefixes: packages/api/src/modules/outreach/, packages/api/src/services/outreach/, packages/api/src/modules/{social,push}/
key_files: modules/outreach/*.routes|service, jobs/workers/outreach{Import,Segment,Compose,Send,Push}.worker.ts, journey.worker.ts, social.worker.ts, queue.ts outreach* + socialPublish/socialMetrics queues, ChannelHealth/EmailSendingDomain/SuppressionEntry models
entrypoints: /api/outreach (sub-routers segments/journeys/email-domains/push mount BEFORE the catch-all), public tracking/unsubscribe routes, /api/social, /api/push.
responsibilities: contact-list import, AI compose, rate-limited send (one recipient per job, delay-chained), A/B variants, journey enrollment/ticks, tracked links, suppression + MarketingConsent (GDPR), social publishing fan-out per target.
invariants: segment_enter enrolls each contact ONCE not every tick (3b6f-era campify fix carried forward); open-click redirect guard (fe24a94); consent gating.
pitfalls: this module was Campify rebuilt — old standalone app deleted; don't resurrect references from docs of that era.
confidence: strongly_inferred (module internals not read line-by-line)

## Files (40+)

- `packages/api/src/modules/outreach/campaign.controller.ts`
- `packages/api/src/modules/outreach/campaign.schemas.ts`
- `packages/api/src/modules/outreach/campaign.service.ts`
- `packages/api/src/modules/outreach/emailDomain.controller.ts`
- `packages/api/src/modules/outreach/emailDomain.routes.ts`
- `packages/api/src/modules/outreach/emailDomain.schemas.ts`
- `packages/api/src/modules/outreach/emailDomain.service.ts`
- `packages/api/src/modules/outreach/journey.controller.ts`
- `packages/api/src/modules/outreach/journey.routes.ts`
- `packages/api/src/modules/outreach/journey.schemas.ts`
- `packages/api/src/modules/outreach/journey.service.ts`
- `packages/api/src/modules/outreach/outreach.controller.ts`
- `packages/api/src/modules/outreach/outreach.public.routes.ts`
- `packages/api/src/modules/outreach/outreach.routes.ts`
- `packages/api/src/modules/outreach/outreach.schemas.ts`
- `packages/api/src/modules/outreach/outreach.service.ts`
- `packages/api/src/modules/outreach/segment.controller.ts`
- `packages/api/src/modules/outreach/segment.routes.ts`
- `packages/api/src/modules/outreach/segment.schemas.ts`
- `packages/api/src/modules/outreach/segment.service.test.ts`
- `packages/api/src/modules/outreach/segment.service.ts`
- `packages/api/src/services/outreach/channelPolicy.push.test.ts`
- `packages/api/src/services/outreach/channelPolicy.ts`
- `packages/api/src/services/outreach/columnMapping.ts`
- `packages/api/src/services/outreach/deliver.ts`

## API surface

- `POST /:id/verify`
- `DELETE /:id`
- `GET /:id`
- `POST /`
- `GET /`
- `GET /:id/stats`
- `POST /:id/enroll`
- `POST /:id/status`
- `PUT /:id`
- `POST /webhooks/email/:orgId`
- `GET /t/c/:token`
- `GET /t/o/:recipientId`
- `GET /u/:token`
- `POST /channel-health/:id/resume`
- `GET /channel-health`
