---
cortex-generated: true
title: page-sections-components
tags: [module]
---

# Page sections & components

**Project:** [[faraj]] | **Confidence:** inferred | **verified@** ``
**Owns:** `src/sections/,src/components/`

purpose: the seven page sections and their building-block components.
path_prefixes: src/sections/, src/components/
key_files: src/sections/{Hero,Work,Services,Approach,Stack,About,Contact}.tsx; src/components/ui/{Reveal,RotatingWord,Marquee,ScrollProgress...}; src/components/work/FeaturedWork.tsx; src/components/layout/Nav.tsx (scroll-spy), LocaleSwitch.tsx (`scroll={false}` to preserve position on switch — README.md:43-44)
entrypoints: composed only by src/app/[locale]/page.tsx
responsibilities: presentation only; narrative order "proof before pitch" documented inline (page.tsx:35-38)
invariants: motion = CSS + IntersectionObserver only, no JS animation libs
pitfalls: Reveal-style components start at opacity:0 — any new animated element must respect the noscript override
confidence: high

## Files (22+)

- `src/components/brand/Logo.tsx`
- `src/components/brand/Wordmark.tsx`
- `src/components/layout/Atmosphere.tsx`
- `src/components/layout/Footer.tsx`
- `src/components/layout/LocaleSwitch.tsx`
- `src/components/layout/Nav.tsx`
- `src/components/layout/ScrollProgress.tsx`
- `src/components/ui/Arrow.tsx`
- `src/components/ui/Chip.tsx`
- `src/components/ui/Marquee.tsx`
- `src/components/ui/Reveal.tsx`
- `src/components/ui/RotatingWord.tsx`
- `src/components/ui/SectionHeader.tsx`
- `src/components/ui/StatusPill.tsx`
- `src/components/work/FeaturedWork.tsx`
- `src/sections/About.tsx`
- `src/sections/Approach.tsx`
- `src/sections/Contact.tsx`
- `src/sections/Hero.tsx`
- `src/sections/Services.tsx`
- `src/sections/Stack.tsx`
- `src/sections/Work.tsx`
