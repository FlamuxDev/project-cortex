---
cortex-generated: true
title: outreach-campaign-manager
tags: [module]
---

# outreach / Campaign Manager

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Models: ContactList→OutreachContact (raw columns preserved verbatim, AI enrichment, dedupeKey, audienceType cold|engaged), Campaign (***REDACTED-B64***), CampaignRecipient (per-recipient generated content + engagement timestamps), Segment (rule DSL), CampaignVariant (A/B), Journey/JourneyRun (node DAG engine), TrackedLink, SuppressionEntry, MarketingConsent, ChannelHealth (warmup + kill-switch), EmailSendingDomain (SPF/DKIM/DMARC), WhatsAppTemplate (`schema.prisma:1291-1710`).
- Send safety spine in `services/outreach/safety/*`: suppression hard gate, consent basis check, content screening, warmup caps, channel health pause. Five dedicated queues + journey tick; send orchestrator self-rate-limits by chaining delayed jobs (`addOutreachSendJob` comment, `queue.ts:61-71`).
- Feature-flagged per org (`outreach.campaigns`, autopilot flag noted in schema comment 1386-1388).

