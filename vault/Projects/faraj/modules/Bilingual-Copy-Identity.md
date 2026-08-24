---
cortex-generated: true
title: bilingual-copy-identity
tags: [module]
---

# Bilingual copy & identity

**Project:** [[faraj]] | **Confidence:** inferred | **verified@** ``
**Owns:** `src/lib/content/,src/lib/site.ts`

purpose: all user-facing prose and identity data, type-enforced bilingual.
path_prefixes: src/lib/content/, src/lib/site.ts
key_files: src/lib/site.ts:8-41 (`site`, `sectionIds` — drives scroll-spy order), src/lib/content/types.ts (SectionCopy/Fact/Stat shapes), src/lib/content/index.ts
entrypoints: imported by sections, seo.ts, sitemap.ts
responsibilities: adding a string requires both languages or TS fails; adding a section = content module → section component → `sectionIds` entry → render in page.tsx (README.md:79-81)
invariants: `site.url` is the root of every canonical/hreflang URL (README.md:89-92)
pitfalls: editing copy means touching two language objects; forgetting `sectionIds` breaks scroll-spy
confidence: high

## Files (11+)

- `src/lib/content/about.ts`
- `src/lib/content/approach.ts`
- `src/lib/content/contact.ts`
- `src/lib/content/hero.ts`
- `src/lib/content/index.ts`
- `src/lib/content/services.ts`
- `src/lib/content/stack.ts`
- `src/lib/content/types.ts`
- `src/lib/content/ui.ts`
- `src/lib/content/work.ts`
- `src/lib/site.ts`
