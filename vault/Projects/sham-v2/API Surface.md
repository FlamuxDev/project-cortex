---
cortex-generated: true
title: sham-v2 api
tags: [api/project]
---

# sham-v2 — API Surface

38 routes. Grouped by owning file; every route names its handler.

## `src/app.js`
*module: [[sham-v2/modules/Api-Surface|api-surface]]*

- **POST** `/api/chat` → handleChat
- **GET** `/api/config` → getConfig
- **GET** `/api/health` → getHealth
- **GET** `/api/voice/auth` → getSignedUrl
- **GET** `/api/voice/status` → getVoiceStatus
- **POST** `/api/voice/tools/ask` → handleVoiceAsk
- **GET** `/api/webhooks/whatsapp` → handleVerify
- **POST** `/api/webhooks/whatsapp`

## `src/channels/http/middlewares.js`
*module: [[sham-v2/modules/Api-Surface|api-surface]]*

- **GET** `X-Admin-Key`

## `src/channels/whatsapp/webhook.js`
*module: [[sham-v2/modules/Meta-Webhook-Queue-Worker|meta-webhook-queue-worker]]*

- **GET** `X-Hub-Signature-256`

## `src/db/mirror.js`
*module: [[sham-v2/modules/Catalog-Generations-Semantic-Layer|catalog-generations-semantic-layer]]*

- **GET** `teacher_more_info`
- **GET** `users`

## `src/sync/import-backup.js`
*module: [[sham-v2/modules/Pgdmp-Import-Pipeline-Accuracy-Harness|pgdmp-import-pipeline-accuracy-harness]]*

- **GET** `cities`
- **GET** `cities`
- **GET** `countries`
- **GET** `districts`
- **GET** `districts`
- **GET** `governorates`
- **GET** `governorates`
- **GET** `grade_levels`
- **GET** `institution_details`
- **GET** `institution_types`
- **GET** `institutions`
- **GET** `posts`
- **GET** `specializations`
- **GET** `sub_districts`
- **GET** `teacher_districts`
- **GET** `teacher_grade_levels`
- **GET** `teacher_more_info`
- **GET** `teacher_specializations`
- **GET** `university_majors`
- **GET** `user_reviews`
- **GET** `users`
- **GET** `users`

## `test/eval/run.js`
*module: [[sham-v2/modules/Pgdmp-Import-Pipeline-Accuracy-Harness|pgdmp-import-pipeline-accuracy-harness]]*

- **GET** `concurrency`
- **GET** `id`
- **GET** `limit`
- **GET** `suite`
