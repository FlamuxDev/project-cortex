---
cortex-generated: true
title: test-ai
tags: [project]
---

# TEST AI

**Path:** `/home/aboud/Dev/TEST AI`  
**Kind:** app | **Languages:** .py,.sql,.js | **Frameworks:** None

**HEAD:** `ec5e16f84200` | **Brain:** `ec5e16f84200` | FRESH

| Files | Symbols | Modules | Flows | APIs | DB | Tests | Decisions | Memories |
|---|---|---|---|---|---|---|---|---|
| 95 | 1055 | 10 | 5 | 36 | 97 | 29 | 7 | 18 (0 stale) |

## Examiner pages
- [[test-ai/API Surface|API Surface]]
- [[test-ai/Code Map|Code Map]]
- [[test-ai/Database|Database]]
- [[test-ai/Flows|Flows]]
- [[test-ai/History & Hotspots|History & Hotspots]]
- [[test-ai/Test Map|Test Map]]

## Pitfalls & rules (memories)
- Historical lessons [verified]
- Risks & technical debt [verified]

## Modules
- [[test-ai/modules/Class-Level-Defect-Hunters|class-level defect hunters]] — One script per bug family so regressions are caught by category, not by incident report. [inferred]
- [[test-ai/modules/Deterministic-Domain-Routing-Entity-Resolution|deterministic domain routing + entity resolution]] — Map a question to one of 8 domains and resolve mentioned places/institutions with thresholds instead [inferred]
- [[test-ai/modules/Honest-Numbers-Out|honest numbers out]] — Compute everything deterministically, render the answer from a fact sheet only, and reject invented  [inferred]
- [[test-ai/modules/Language-Understanding-Without-A-Model|language understanding without a model]] — Arabic normalization, language detection, synonym/respelling tolerance. [inferred]
- [[test-ai/modules/Nightly-Data-Swap|nightly data swap]] — Restore the freshest verified directory dump from S3 without ever applying the same file twice. [inferred]
- [[test-ai/modules/Ops-Through-Conversation|ops-through-conversation]] — Let staff verify institutions/teachers through WhatsApp flows backed by the Shamsieh admin API. [inferred]
- [[test-ai/modules/Queryspec-Engine|QuerySpec engine]] — Turn natural language into safe parameterized SQL via structured spec + deterministic validator/comp [inferred]
- [[test-ai/modules/Request-Lifecycle|request lifecycle]] — Orchestrate one turn end-to-end with outcome classification (answered/smalltalk/refused/clarified/pl [inferred]
- [[test-ai/modules/Trace-Logbook-Judge-Dashboard|trace / logbook / judge / dashboard]] — Record every turn, classify outcomes, judge correctness from production traffic, surface it all in a [inferred]
- [[test-ai/modules/Whatsapp-Voice-Web|whatsapp / voice / web]] — Carry the agent to users where they already are. [inferred]

## Flows
- **ask-turn (web/api)** — POST /ask {question, session_id?, lat/lon?, user.countryId?}
- **whatsapp-turn** — Meta webhook POST with X-Hub-Signature-256
- **voice-call** — ElevenLabs Conversational AI calls /voice/chat/completions (custom LLM) with VOICE_API_KEY header
- **nightly-directory-refresh** — systemd timer 03:30 Asia/Amman (dump produced 03:00)
- **problem-report** — POST /report from web UI

## Key knowledge
- Architecture [strongly_inferred]
- Database [strongly_inferred]
- API surface [strongly_inferred]
- Historical lessons [verified]
- TEST AI: overview [verified]
- Tests & commands [verified]
