---
cortex-generated: true
title: lifecycle-reminders-outbound
tags: [module]
---

# Lifecycle/reminders/outbound

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `packages/backend/src/application/messaging/,application/booking/book-appointment.ts`

purpose: post-booking confirmations, cron reminders, template rendering, deposit gating.
path_prefixes: packages/backend/src/application/messaging/, application/booking/book-appointment.ts
key_files: reminders.ts (`runAppointmentReminders`, offsets default [24,2]h ±45min window, atomic claim on appointments.reminders_sent JSONB `__pending__`→ISO ts, released on failure), lifecycle.ts (confirmation skip for pending_deposit/cancelled; re-exports deposit.ts intentionally), outbound.ts (org templates ▸ bilingual fallback render), templates.ts, deposit.ts (owns schema access), ../booking/book-appointment.ts (`bookAppointment` use-case fires notifyAppointmentBooked)
invariants: parallel cron runs cannot double-send (atomic claim); confirmation sent once per appointment
pitfalls: broken-import regression guard exists as deposit.test.ts
confidence: high

## Files (8+)

- `packages/backend/src/application/booking/book-appointment.ts`
- `packages/backend/src/application/messaging/deposit.test.ts`
- `packages/backend/src/application/messaging/deposit.ts`
- `packages/backend/src/application/messaging/lifecycle.ts`
- `packages/backend/src/application/messaging/outbound.ts`
- `packages/backend/src/application/messaging/reminders.test.ts`
- `packages/backend/src/application/messaging/reminders.ts`
- `packages/backend/src/application/messaging/templates.ts`
