---
cortex-generated: true
title: auth-session-dashboard-identity
tags: [module]
---

# auth & session (dashboard identity)

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Paths: `modules/auth/*`, `middleware/auth.ts`, `middleware/platformAuth.ts`, `middleware/platformSuper.ts`.
- Login: bcrypt(12) compare; per-account lockout counters in Redis with in-process fallback (`auth.service.ts:36-93`); email OR phone lookup (`auth.service.ts:367-384`); unverified email and suspended/deleted org rejected. Tokens: 15m access JWT + 7d refresh JWT (refresh stored single-copy in Redis `refresh:{userId}`, rotated each refresh, `auth.service.ts:97-144,431-475`); payload carries `tv` tokenVersion — bumped on password reset/sign-out-all/org suspension to invalidate cluster-wide (`auth.service.ts:602-634`, schema comment `schema.prisma:95-97`). `authenticate` re-reads the user each request and checks `tokenVersion`, `disabledAt`, org `deletedAt`/`status` in one query (`middleware/auth.ts:43-70`).
- Authorization: string permissions resolved from non-expired `UserRole→Role→RolePermission`; org owner bypasses (`authorize`, `middleware/auth.ts:102-140`); `authorizeAny` for OR-semantics; support-inbox permission implied by agents:create/update/delete (`userSatisfiesPermission`, `middleware/auth.ts:9-19`).
- Invariant: expired role assignments must never grant permissions (`activeUserRoleWhere`, `middleware/auth.ts:95-100`).
- Platform admin auth is a fully separate identity + middleware chain (`modules/platform/platform-auth*.ts`, `middleware/platformAuth.ts`).

