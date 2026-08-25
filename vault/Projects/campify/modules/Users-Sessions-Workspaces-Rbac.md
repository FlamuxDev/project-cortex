---
cortex-generated: true
title: users-sessions-workspaces-rbac
tags: [module]
---

# users, sessions, workspaces, RBAC

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `packages/core/src/identity,apps/api/src/app.ts (auth+workspace routes)`

purpose: signup/verify/login/logout, sessions, memberships, invitations, the RBAC matrix.
path_prefixes: packages/core/src/identity, apps/api/src/app.ts (auth+workspace routes)
key_files: packages/core/src/identity/service.ts, rbac.ts, password.ts (scrypt), emails.ts; apps/api/src/app.ts
entrypoints: POST /v1/auth/*, /v1/me, /v1/workspaces, invitations/members routes; assertCan()/can() used by every handler
responsibilities: opaque server-side session tokens (hash-stored), scrypt passwords, six-role × permission matrix asserted cell-by-cell against PRD §20.3; invitation tokens bound to accepting user's address, `on conflict do nothing` so an invitation can never mutate an existing membership.
invariants: only an owner may grant/revoke owner (enforced in changeRole, removeMember AND inviteMember — partial hardening produced a takeover, commit ea32541); last-owner demotion guarded INSIDE the UPDATE/DELETE after `select … for update`; non-member sees 404 not 403 (workspace existence is a leak); verification/invite tokens never returned to callers in prod.
pitfalls: global tables (users/sessions) run outside tenant scope by design; auth throttles are tight (signup 5/min) and unauthenticated ones key on req.ip — bites any test minting many accounts (PROGRESS.md M18).
confidence: verified

## Files (6+)

- `packages/core/src/identity/emails.ts`
- `packages/core/src/identity/emails.unit.test.ts`
- `packages/core/src/identity/password.ts`
- `packages/core/src/identity/rbac.ts`
- `packages/core/src/identity/rbac.unit.test.ts`
- `packages/core/src/identity/service.ts`
