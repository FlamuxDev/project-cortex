---
cortex-generated: true
title: locales-dictionaries
tags: [module]
---

# locales & dictionaries

**Project:** [[umbrellaprime]] | **Confidence:** inferred | **verified@** `b56420dad197`
**Owns:** `src/lib/i18n.ts,src/content/`

purpose: typed ar/en dictionaries, direction, trailing-slash-aware hrefs.
path_prefixes: src/lib/i18n.ts, src/content/
key_files: src/lib/i18n.ts:29-38 (`localeHref` keeps trailing slash + preserves #hash), src/content/ar.ts & en.ts (Dictionary type exported from en.ts, ar must satisfy it structurally)
entrypoints: every layout/page imports getDictionary(locale)
responsibilities: defaultLocale = "ar"; alternateLocale map for switcher/hreflang
invariants: all internal links go through localeHref (slash contract required by S3 key layout)
pitfalls: Dictionary type lives in en.ts — adding a field to en but not ar fails only where ar is consumed as Dictionary [inferred]
confidence: high

## Files (3+)

- `src/content/ar.ts`
- `src/content/en.ts`
- `src/lib/i18n.ts`
