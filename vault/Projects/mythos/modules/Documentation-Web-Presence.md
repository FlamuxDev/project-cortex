---
cortex-generated: true
title: documentation-web-presence
tags: [module]
---

# Documentation & web presence

**Project:** [[mythos]] | **Confidence:** inferred | **verified@** `15e9faf0b5db`
**Owns:** `website/,mythos-web/,mythos-docs/,docs/`

purpose: user/developer docs (Docusaurus), marketing/install site, and the internal AI-authored build-spec package.
path_prefixes: website/, mythos-web/, mythos-docs/, docs/
key_files: mythos-docs/00-MASTER-build-spec.md + 01–14 (architecture, cloud API, DB schema, sandbox, privacy, i18n/RTL, rebrand checklist, testing), mythos-web/package.json ("safaeb"), website/docs/** (published docs source)
entrypoints: deploy-site.yml (Vercel hook) / GH Pages; npm build per site
responsibilities: extract-skills/generate-skill-docs scripts sync skill docs into site; Arabic localization + RTL (i18n toggle, git a246e5c/f1243ca)
confidence: medium-high

## Files (39+)

- `mythos-web/src/App.tsx`
- `mythos-web/src/anim/primitives.tsx`
- `mythos-web/src/api.ts`
- `mythos-web/src/components/AuthShell.tsx`
- `mythos-web/src/components/ConnectorsStrip.tsx`
- `mythos-web/src/components/CookieConsent.tsx`
- `mythos-web/src/components/Features.tsx`
- `mythos-web/src/components/FinalCTA.tsx`
- `mythos-web/src/components/Footer.tsx`
- `mythos-web/src/components/Hero.tsx`
- `mythos-web/src/components/HowItWorks.tsx`
- `mythos-web/src/components/LegalLayout.tsx`
- `mythos-web/src/components/LiveDemo.tsx`
- `mythos-web/src/components/Logo.tsx`
- `mythos-web/src/components/Nav.tsx`
- `mythos-web/src/main.tsx`
- `mythos-web/src/pages/Account.tsx`
- `mythos-web/src/pages/Cookies.tsx`
- `mythos-web/src/pages/Docs.tsx`
- `mythos-web/src/pages/Download.tsx`
- `mythos-web/src/pages/Landing.tsx`
- `mythos-web/src/pages/Login.tsx`
- `mythos-web/src/pages/Pair.tsx`
- `mythos-web/src/pages/Pricing.tsx`
- `mythos-web/src/pages/Privacy.tsx`

## API surface

- `GET next`
- `GET code`
