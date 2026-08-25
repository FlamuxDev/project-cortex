---
cortex-generated: true
title: consent-compliance-gdpr
tags: [module]
---

# consent / compliance / GDPR

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Widget GDPR consent ledger `ConsentRecord` (policyVersion, IP/UA) from banner/public endpoint (`schema.prisma:410-428`, `organizations/consent.routes.ts`).
- Right-to-access export capped at 5000 conversations excluding secrets/vectors; RTBF flows for identity memory (`gdpr.service.ts:1-40`, identity RTBF above). Compliance JSONB on AgentConfig gates public rating/transcript-export/disclosure server-side (`chat.routes.ts:115-133` comments FR-26/FR-27).

