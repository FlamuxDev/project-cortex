---
cortex-generated: true
title: notifications-audit-logs
tags: [module]
---

# notifications & audit logs

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- In-app Notification rows + Socket.IO `notification:new` to user rooms (`emitUserNotification`, conversationRealtime.ts:140-156); email via Resend/Nodemailer (`services/email`); web-push delivery.
- `AuditLog` with orgId scope for tenant-readable trails (`schema.prisma:1152-1171`), written by `logAudit` across identity/Odoo/GDPR flows; retention swept by `auditRetention.worker.ts`. Separate OdooAuditEvent table for that connector.

