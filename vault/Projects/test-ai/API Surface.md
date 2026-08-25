---
cortex-generated: true
title: test-ai api
tags: [api/project]
---

# TEST AI — API Surface

36 routes. Grouped by owning file; every route names its handler.

## `agent/api.py`

- **GET** `/` → index
- **POST** `/admin/judge/run` → admin_judge
- **POST** `/admin/voicesync/run` → admin_voicesync
- **POST** `/ask` → ask
- **POST** `/ask/debug` → ask_debug
- **GET** `/dashboard` → dashboard
- **GET** `/dashboard-app.js` → dashboard_app_js
- **GET** `/dashboard.css` → dashboard_css
- **GET** `/dashboard.js` → dashboard_js
- **GET** `/health` → health_check
- **POST** `/report` → file_report
- **GET** `/reports/analytics` → report_analytics
- **GET** `/reports/conversation/{session_id}` → report_conversation
- **GET** `/reports/conversations` → report_conversations
- **POST** `/reports/custom` → report_custom
- **GET** `/reports/notes` → report_notes
- **GET** `/reports/notes/{note_id}/image` → report_note_image
- **POST** `/reports/notes/{note_id}/status` → report_note_status
- **GET** `/reports/problems` → report_problems
- **GET** `/reports/quality` → report_quality
- **GET** `/reports/saved` → report_saved
- **POST** `/reports/saved` → report_save
- **DELETE** `/reports/saved/{name}` → report_unsave
- **GET** `/reports/summary` → report_summary
- **GET** `/reports/top_questions` → report_top_questions
- **GET** `/reports/unanswered` → report_unanswered
- **GET** `/reports/vocabulary` → report_vocabulary
- **GET** `/reports/voice` → report_voice
- **GET** `/reports/voice_calls` → report_voice_calls
- **DELETE** `/session/{session_id}` → reset
- **GET** `/stats` → stats
- **GET** `/traces` → traces
- **GET** `/traces/{trace_id}` → one_trace
- **POST** `/voice/chat/completions` → voice_chat
- **GET** `/whatsapp/webhook` → whatsapp_verify
- **POST** `/whatsapp/webhook` → whatsapp_webhook
