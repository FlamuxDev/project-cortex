---
cortex-generated: true
title: next-js-app-marketing-auth-console
tags: [module]
---

# Next.js app (marketing + auth + console)

**Project:** [[telvora]] | **Confidence:** verified | **verified@** `7423f040ed46`
**Owns:** `apps/web/src/app/(marketing|(auth|protected))/[locale]/*,apps/web/src/lib/*,apps/web/src/proxy.ts`

purpose: bilingual (en/ar RTL) public site, auth screens, and the full operator console (~74 routes)
path_prefixes: apps/web/src/app/(marketing|(auth|protected))/[locale]/*, apps/web/src/lib/*, apps/web/src/proxy.ts
key_files: src/lib/guard.ts (server-side enforcement), src/lib/redirectUrl.ts (proxy-safe redirects), src/proxy.ts (locale negotiation), navItems.ts (grouped IA)
entrypoints: `next dev/build/start` :3000
responsibilities: server components fetch core-api via lib clients using session bearer token; form actions POST then redirect via redirectUrl()
invariants: hidden navigation is not authorization — requireSession on every protected page; NEXT_PUBLIC_APP_URL must be baked as build arg for canonical/SEO + redirect base (7423f04)
pitfalls: request.url origin is localhost under `next start` behind proxies — never build redirect URLs from it (99-file lesson)
confidence: verified

## Files (1+)

- `apps/web/src/proxy.ts`
