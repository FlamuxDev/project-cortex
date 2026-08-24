---
cortex-generated: true
title: tauri-wrapper
tags: [module]
---

# Tauri wrapper

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `apps/desktop/`

purpose: native window over hosted web app; deep links return OAuth/billing flows to web destinations.
path_prefixes: apps/desktop/
key_files: src-tauri/src/lib.rs (deep_link_to_web_url, tray, shortcuts, autostart, DesktopPreferences JSON persistence), src-tauri/tauri.conf.json, shell/index.html (loading placeholder)
invariants: v1 is hosted-URL shell — no local backend; release builds hardcode PRODUCTION_APP_URL
confidence: high

## Files (2+)

- `apps/desktop/scripts/tauri-prereq-checker.mjs`
- `apps/desktop/scripts/tauri-prereq-checker.test.mjs`
