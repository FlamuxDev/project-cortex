---
cortex-generated: true
title: booking-demo-scheduler
tags: [module]
---

# booking (demo scheduler)

**Project:** [[chat-agent-saas]] | **Confidence:** inferred | **verified@** `d5c6955acca7`
**Owns:** ``

- Platform-owned single-row settings (`DemoBookingSettings` id="default", availability JSON array of weekly rules, fixed UTC offset — Gulf no-DST rationale at `schema.prisma:200-203`). Public slot listing + confirm create `DemoAppointment`, send owner/customer emails (`modules/booking/booking.service.ts:81-120`, `booking.public.routes.ts`). Admin surface rides on platform routes.

