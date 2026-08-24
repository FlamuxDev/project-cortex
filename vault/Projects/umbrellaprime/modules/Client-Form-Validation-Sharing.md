---
cortex-generated: true
title: client-form-validation-sharing
tags: [module]
---

# client form + validation sharing

**Project:** [[umbrellaprime]] | **Confidence:** inferred | **verified@** `b56420dad197`
**Owns:** `src/components/forms/ContactForm.tsx,src/lib/validation.ts`

purpose: accessible bilingual form posting directly to Lambda.
path_prefixes: src/components/forms/ContactForm.tsx, src/lib/validation.ts
key_files: ContactForm.tsx:36-83 (SubmitState machine incl. honest not-configured state; honeypot field pretends success without sending; success ONLY when Lambda answers {status:"sent"}), validation.ts:4-19 (buildContactSchema takes localized error MESSAGES so one schema serves both languages; consent literal("true"); phone digit-count refine; honeypot max(0))
entrypoints: rendered by /[locale]/contact/page.tsx
responsibilities: native HTML validation layered under Zod; NEXT_PUBLIC_CONTACT_API_URL read at build time (static export)
invariants: never fake success; honeypot hidden via clip technique chosen after off-canvas offset caused horizontal overflow (comment at line 87)
pitfalls: env var is baked at build — changing Lambda URL requires rebuild
confidence: high

## Files (2+)

- `src/components/forms/ContactForm.tsx`
- `src/lib/validation.ts`
