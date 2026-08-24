---
cortex-generated: true
title: google-microsoft-account-integrations
tags: [module]
---

# Google/Microsoft account integrations

**Project:** [[mythos]] | **Confidence:** inferred | **verified@** `15e9faf0b5db`
**Owns:** `agent/connectors/,agent/google_connector_oauth.py,agent/microsoft_connector_oauth.py,tools/connector_tool.py`

purpose: first-class calendar/email/tasks/drive/contacts tools with OAuth.
path_prefixes: agent/connectors/, agent/google_connector_oauth.py, agent/microsoft_connector_oauth.py, tools/connector_tool.py
key_files: agent/connectors/google_{calendar,contacts,drive,gmail,tasks}.py, ms_{calendar,todo,outlook,onedrive}.py, shared _google_http/_ms_http
entrypoints: connector tool surfaced to agent; dashboard /api/connections OAuth flows
responsibilities: token refresh, explicit provider choice (ce87003 fixed always-Google bug), id-based update/delete + status vocabulary tolerance (0539422, 0b23d97)
invariants: listed in SHIFT.md as features to preserve completely
confidence: high

## Files (15+)

- `agent/connectors/__init__.py`
- `agent/connectors/_google_http.py`
- `agent/connectors/_ms_http.py`
- `agent/connectors/google_calendar.py`
- `agent/connectors/google_contacts.py`
- `agent/connectors/google_drive.py`
- `agent/connectors/google_gmail.py`
- `agent/connectors/google_tasks.py`
- `agent/connectors/ms_calendar.py`
- `agent/connectors/ms_onedrive.py`
- `agent/connectors/ms_outlook.py`
- `agent/connectors/ms_todo.py`
- `agent/google_connector_oauth.py`
- `agent/microsoft_connector_oauth.py`
- `tools/connector_tool.py`
