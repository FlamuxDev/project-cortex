---
cortex-generated: true
title: tokens-primitives
tags: [module]
---

# tokens & primitives

**Project:** [[umbrellaprime]] | **Confidence:** inferred | **verified@** `b56420dad197`
**Owns:** `src/components/{ui,brand,layout}/,src/app/globals.css`

purpose: navy/gold dark identity, layout primitives, accessibility basics.
path_prefixes: src/components/{ui,brand,layout}/, src/app/globals.css
key_files: globals.css:7-39 (@theme palette + fade-in keyframes), globals.css:51-53 (RTL font swap), globals.css:60-70 (.ltr-embed bidi isolation for numerals/emails in Arabic copy; WCAG focus-visible ring), SkipLink.tsx, LanguageSwitcher.tsx, MobileNavigation.tsx, WhatsAppButton.tsx
entrypoints: imported via root/locale layouts
responsibilities: SectionHeading/Button/Container primitives; ArcMotif/ServiceIcons brand SVGs
invariants: single deliberate dark surface — no light/dark toggle (globals.css:3-6)
confidence: high

## Files (3+)

- `src/components/brand/ArcMotif.tsx`
- `src/components/brand/Logo.tsx`
- `src/components/brand/ServiceIcons.tsx`
