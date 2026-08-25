---
cortex-generated: true
title: transcript-crawler-services
tags: [module]
---

# transcript & crawler services

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Transcript export renders txt/json/pdf (pdfkit) with compliance gating (`services/transcript/transcriptExport.ts`, `chat.service.ts:2521`); size-bounded and origin-checked on the public route (`chat.routes.ts:127-133`).
- Crawler: `services/crawler/` drives URL sources — static fetch by default, puppeteer browser rendering when `renderMode:'browser'` or auto-detected SPA behavior; per-page politeness via safeFetch (SSRF-guarded, response-size/type caps hardened in commit 4a98dde "slow/huge/wrong-type responses").

