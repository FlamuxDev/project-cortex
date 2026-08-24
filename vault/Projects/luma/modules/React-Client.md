---
cortex-generated: true
title: react-client
tags: [module]
---

# React client

**Project:** [[luma]] | **Confidence:** inferred | **verified@** `da7bced5651b`
**Owns:** `LUMA_FontEnd/src/`

purpose: landing page, auth flows (register/login/verify/reset), workspace dashboard, live blueprint creation/viewer with SSE progress, admin console (Users, Logs, SystemState, Settings, Overview).
path_prefixes: LUMA_FontEnd/src/
key_files: src/App.jsx, src/api/api.js, src/page/new-blueprint.jsx, src/page/Workspace.jsx, src/i18n.jsx
entrypoints: vite dev server; routes in App.jsx (/login, /Work, /new-blueprint, /newblueprint2, /DualWorkspace, admin paths)
responsibilities: axios instance with token interceptor (accessToken w/ legacy `token` fallback), EventSource subscription to blueprint events (new-blueprint.jsx:2578), markdown rendering (react-markdown + remark-gfm), dark mode toggle.
invariants: talks only to backend base URL `VITE_API_URL || https://api.luma-agent.com/api`.
pitfalls: token in localStorage + console.logs of auth headers (api.js:30-58); no tests; mega-components (new-blueprint.jsx >2,500 lines).
confidence: high

## Files (23+)

- `LUMA_FontEnd/src/App.jsx`
- `LUMA_FontEnd/src/api/api.js`
- `LUMA_FontEnd/src/components/Sidebar/Sidebar.jsx`
- `LUMA_FontEnd/src/i18n.jsx`
- `LUMA_FontEnd/src/main.jsx`
- `LUMA_FontEnd/src/page/BlueprintsAdmen.jsx`
- `LUMA_FontEnd/src/page/DualWorkspace.jsx`
- `LUMA_FontEnd/src/page/ForgotPassword.jsx`
- `LUMA_FontEnd/src/page/Login.jsx`
- `LUMA_FontEnd/src/page/Logs.jsx`
- `LUMA_FontEnd/src/page/Overview.jsx`
- `LUMA_FontEnd/src/page/Register.jsx`
- `LUMA_FontEnd/src/page/ResetPassword.jsx`
- `LUMA_FontEnd/src/page/Resources.jsx`
- `LUMA_FontEnd/src/page/Settings.jsx`
- `LUMA_FontEnd/src/page/SystemState.jsx`
- `LUMA_FontEnd/src/page/Users.jsx`
- `LUMA_FontEnd/src/page/VerifyEmail.jsx`
- `LUMA_FontEnd/src/page/Workspace.jsx`
- `LUMA_FontEnd/src/page/home.jsx`
- `LUMA_FontEnd/src/page/landing-page.jsx`
- `LUMA_FontEnd/src/page/new-blueprint.jsx`
- `LUMA_FontEnd/src/page/newblueprint2.jsx`

## API surface

- `GET /admin/blueprints`
- `GET id`
- `POST /auth/forgot-password`
- `POST /auth/login`
- `GET /admin/blueprints?limit=10&sort=created_at:desc`
- `POST /auth/register`
- `POST /auth/reset-password`
- `GET /blueprints?status=completed&limit=12`
- `GET /super-admin/system-stats`
- `GET /admin/users`
- `POST /auth/resend-otp`
- `POST /auth/verify-otp`
- `GET /blueprints`
- `DELETE /users/account`
- `POST /auth/logout`
