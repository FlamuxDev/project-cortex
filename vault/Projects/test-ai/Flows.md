---
cortex-generated: true
title: test-ai flows
tags: [flows/project]
---

# TEST AI — Product Flows

End-to-end behaviors as verified from source. Files are the evidence trail.

## ask-turn (web/api)
**Trigger:** POST /ask {question, session_id?, lat/lon?, user.countryId?}
*[[test-ai]] · confidence: high*

trigger: POST /ask {question, session_id?, lat/lon?, user.countryId?}
steps: country resolution → normalize → resolve entities (short-circuit KNOWN_ABSENT/NOT_FOUND/AMBIGUOUS with one Gemini clarify) → route domain → fastpath (count questions: zero LLM) else plan(QuerySpec) → validate(9 checks) → compile → execute as ai_reader → facts compute → answer generate from fact sheet → number-guard → suggestions generated in same call → trace recorded → response {answer, outcome, institutions[], suggestions[], trace_id, latency_ms, tokens}.
files: agent/pipeline.py, agent/plan.py, agent/compile.py, agent/facts.py, agent/answer.py, agent/api.py
confidence: high

**Files:**
- `agent/pipeline.py`
- `agent/plan.py`
- `agent/compile.py`
- `agent/facts.py`
- `agent/answer.py`
- `agent/api.py`

## whatsapp-turn
**Trigger:** Meta webhook POST with X-Hub-Signature-256
*[[test-ai]] · confidence: high*

trigger: Meta webhook POST with X-Hub-Signature-256
steps: HMAC verify against WHATSAPP_APP_SECRET → parse messages → session mapped from wa_id → same Agent.ask → text transformed (tables→WhatsApp formatting, split ≤3900) → Graph API send + mark_read; unsupported types get localized notice; voice notes/media handled or politely refused.
files: agent/whatsapp.py, agent/api.py
confidence: high

**Files:**
- `agent/whatsapp.py`
- `agent/api.py`

## voice-call
**Trigger:** ElevenLabs Conversational AI calls /voice/chat/completions (custom LLM) with VOICE_API_KEY header
*[[test-ai]] · confidence: high*

trigger: ElevenLabs Conversational AI calls /voice/chat/completions (custom LLM) with VOICE_API_KEY header
steps: derive question + session from payload → Agent.ask → fact sheet trimmed to SPOKEN_ROWS(3) → digits/domains spelled, internal notes dropped, greeting suppression rule → SSE chunks streamed back; voicesync keeps ElevenLags agent config aligned via tools/voice_setup.py.
files: agent/voice.py, agent/voicesync.py, tools/voice_setup.py
confidence: high

**Files:**
- `agent/voice.py`
- `agent/voicesync.py`
- `tools/voice_setup.py`

## nightly-directory-refresh
**Trigger:** systemd timer 03:30 Asia/Amman (dump produced 03:00)
*[[test-ai]] · confidence: high*

trigger: systemd timer 03:30 Asia/Amman (dump produced 03:00)
steps: LIST bucket (SigV4 signed query) → pick newest passing pattern/age(≥30min)/size(≥50MB) → ETag ≠ last applied else exit idempotently → stream download → restore into scratch DB → verify row counts → apply views/functions → atomic swap live↔scratch.
files: agent/refresh.py, deploy/shamsieh-refresh.service, deploy/shamsieh-refresh.timer
confidence: high

**Files:**
- `agent/refresh.py`
- `deploy/shamsieh-refresh.service`
- `deploy/shamsieh-refresh.timer`

## problem-report
**Trigger:** POST /report from web UI
*[[test-ai]] · confidence: high*

trigger: POST /report from web UI
steps: rate-limit per session (5/10min) → description required → image sniffed (PNG/JPEG/WEBP/GIF, size caps) → stored as note → surfaced in /reports/notes with status transitions and image endpoint.
files: agent/api.py, agent/reports.py
confidence: high

**Files:**
- `agent/api.py`
- `agent/reports.py`
