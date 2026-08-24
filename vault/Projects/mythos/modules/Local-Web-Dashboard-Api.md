---
cortex-generated: true
title: local-web-dashboard-api
tags: [module]
---

# Local web dashboard + API

**Project:** [[mythos]] | **Confidence:** inferred | **verified@** `15e9faf0b5db`
**Owns:** `web/,safa_cli/web_server.py,safa_localserver/`

purpose: localhost SPA managing config/sessions/skills/cron/plugins/profiles/analytics + chat via embedded TUI.
path_prefixes: web/, safa_cli/web_server.py, safa_localserver/
key_files: web/src/App.tsx, web/src/pages/* (20 pages: Chat, Sessions, Skills, Cron, Workspace, Analytics…), safa_cli/web_server.py (FastAPI, ~4.2k LOC), safa_localserver/account_api.py, workspace_api.py, localtoken.py
entrypoints: `safa dashboard` (binds 127.0.0.1; docker-compose keeps it localhost-only)
responsibilities: REST `/api/*` (config, env vars, sessions+search, cron CRUD, profiles, plugins hub, OAuth connections, logs), `/api/pty` WebSocket (token via query param), static serving of web_dist
invariants: ephemeral _SESSION_TOKEN auth; browsers can't set Authorization on WS upgrade → query-param token; PTY frames raw bytes, resize via `\x1b[RESIZE:c;r]` escape
pitfalls: exposing on LAN without auth is unsafe (stores API keys) — docker-compose comments forbid --host 0.0.0.0
confidence: high

## Files (40+)

- `safa_cli/web_server.py`
- `safa_localserver/__init__.py`
- `safa_localserver/account_api.py`
- `safa_localserver/localtoken.py`
- `safa_localserver/workspace_api.py`
- `web/eslint.config.js`
- `web/src/App.tsx`
- `web/src/components/AnimatedNumber.tsx`
- `web/src/components/AutoField.tsx`
- `web/src/components/Backdrop.tsx`
- `web/src/components/ChatSidebar.tsx`
- `web/src/components/CommandPalette.tsx`
- `web/src/components/ConnectionsSection.tsx`
- `web/src/components/DeleteConfirmDialog.tsx`
- `web/src/components/InspectorPanel.tsx`
- `web/src/components/LanguageSwitcher.tsx`
- `web/src/components/LoadingSkeleton.tsx`
- `web/src/components/Markdown.tsx`
- `web/src/components/ModelInfoCard.tsx`
- `web/src/components/ModelPickerDialog.tsx`
- `web/src/components/NouiTypography.tsx`
- `web/src/components/OAuthLoginModal.tsx`
- `web/src/components/OAuthProvidersCard.tsx`
- `web/src/components/PlatformsCard.tsx`
- `web/src/components/Reveal.tsx`

## API surface

- `GET /api/status`
- `POST /api/gateway/restart`
- `POST /api/mythos/update`
- `GET /api/actions/{name}/status`
- `GET /api/sessions`
- `GET /api/sessions/search`
- `GET /api/config`
- `GET /api/config/defaults`
- `GET /api/config/schema`
- `GET /api/model/info`
- `GET /api/model/options`
- `GET /api/model/auxiliary`
- `POST /api/model/set`
- `PUT /api/config`
- `GET /api/env`
