---
cortex-generated: true
title: whatsapp-voice-web
tags: [module]
---

# whatsapp / voice / web

**Project:** [[test-ai]] | **Confidence:** inferred | **verified@** `ec5e16f84200`
**Owns:** `agent/whatsapp.py,agent/voice.py,agent/voicesync.py,web/`

purpose: Carry the agent to users where they already are.
path_prefixes: agent/whatsapp.py, agent/voice.py, agent/voicesync.py, web/
key_files: agent/whatsapp.py (signature verify, split_message, send_list, media download), agent/voice.py (to_speech transformations, key verify, streaming chunks), web/index.html + dashboard files
entrypoints: FastAPI routes; static pages served by named routes (parameterized asset route was rejected deliberately — api.py comment)
pitfalls: markdown tables don't survive WhatsApp — converted; RTL broke drawer positioning on mobile (75446e2); greeting injected mid-call was a defect (0417f89).
confidence: high

## Files (5+)

- `agent/voice.py`
- `agent/voicesync.py`
- `agent/whatsapp.py`
- `web/dashboard-app.js`
- `web/dashboard.js`
