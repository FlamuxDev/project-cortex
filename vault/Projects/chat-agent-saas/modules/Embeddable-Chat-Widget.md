---
cortex-generated: true
title: embeddable-chat-widget
tags: [module]
---

# Embeddable chat widget

**Project:** [[chat-agent-saas]] | **Confidence:** verified | **verified@** `d5c6955acca7`
**Owns:** `packages/widget/src/`

purpose: dependency-light vanilla-TS embeddable widget: chat, image upload, voice, handoff, per-agent theming; Shadow-DOM isolated.
path_prefixes: packages/widget/src/
key_files: main.ts (sets window.Shamsi after mount), core/{ChatWidget.ts,voice-loader.ts(+test),widget-markdown.ts,widget-settings.ts}, voice-entry.ts, styles/
entrypoints: two Vite lib-mode IIFE builds: widget.iife.js and widget-voice.iife.js (@elevenlabs/client); voice bundle injected by core/voice-loader.ts on FIRST voice call only.
responsibilities: Socket.IO + REST transport to public chat endpoints; draggable position persistence; quick replies, custom CSS; streams errors surfaced (d62ff51 fixed silent swallowing).
invariants: keep the dual-IIFE build — a plain import() cannot replace it because Vite lib-mode forces inlineDynamicImports for single-file IIFE output and would fold the SDK back into the main bundle.
pitfalls: patch_widget*.js / fix_widget.js at repo root are one-off codemods from drag-feature development — historical debris, not product code.
confidence: verified

## Files (11+)

- `packages/widget/src/core/ChatWidget.ts`
- `packages/widget/src/core/voice-loader.test.ts`
- `packages/widget/src/core/voice-loader.ts`
- `packages/widget/src/core/widget-markdown.ts`
- `packages/widget/src/core/widget-message-markup.ts`
- `packages/widget/src/core/widget-settings.ts`
- `packages/widget/src/core/widget.utils.test.ts`
- `packages/widget/src/core/widget.utils.ts`
- `packages/widget/src/main.ts`
- `packages/widget/src/styles/widget.styles.ts`
- `packages/widget/src/voice-entry.ts`
