---
cortex-generated: true
title: tailwind-v4-css-first-theming
tags: [module]
---

# Tailwind v4 CSS-first theming

**Project:** [[faraj]] | **Confidence:** inferred | **verified@** ``
**Owns:** `src/styles/globals.css`

purpose: single source of all colors/radii/type-scale/easings.
path_prefixes: src/styles/globals.css
key_files: globals.css:17-53 (`@theme` literal tokens: void/surface/ink/ember palette with contrast ratios annotated), globals.css:57-63 (`@theme inline` font stacks resolving next/font vars)
entrypoints: imported once in layout
responsibilities: no tailwind.config.ts exists; utilities like `bg-void`/`text-ember` stay in sync with hand-written CSS through shared custom properties (globals.css:12-16)
invariants: flat elevation — all shadow vars explicitly `none` (globals.css:65-72)
pitfalls: brand name drift — README says "Obsidian & Ember", DESIGN.md/globals.css say "OpenClaw Dark"
confidence: high

