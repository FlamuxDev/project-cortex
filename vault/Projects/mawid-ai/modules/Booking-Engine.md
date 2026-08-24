---
cortex-generated: true
title: booking-engine
tags: [module]
---

# Booking engine

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `packages/backend/src/domain/booking/`

purpose: pure-ish business rules for availability and slot-safe writes.
path_prefixes: packages/backend/src/domain/booking/
key_files: rules.ts (`canBookSlot`, cancel/reschedule windows, party size), availability.ts (`getAvailableSlots`, `intervalsOverlap` single source of truth, work-hours), book.ts (`validateAndBookSlot` :296, `applyRescheduleWithSlotLock` :499 owns price-on-reschedule recompute, `acquireSlotBookingLock` :625 = `pg_advisory_xact_lock(hashtext(scope))` inside txn, RRULE `expandRecurringOccurrences` :664, operator-only `skipSlotCheck`), pricing.ts (staff→time_band→vip→flat fallback then offers)
entrypoints: called from application layer + AI tools + dashboard APIs
responsibilities: enforce notice hours, same-day, max advance, party size, staff/resource/group-seat collision
invariants: imports kernel + db only (no ai/messaging/infra/app); paymentsEnabled flag injected by caller — domain does no settings I/O; NO "one active booking per customer/service" rule exists (documented non-feature)
pitfalls: slot lock scope must include the collision dimension or double-booking returns; staff must be linked via staff_services (`ensureDefaultStaffServiceLinks` :635) else `slot_unavailable`
confidence: high

## Files (6+)

- `packages/backend/src/domain/booking/availability.ts`
- `packages/backend/src/domain/booking/book.ts`
- `packages/backend/src/domain/booking/overlap.test.ts`
- `packages/backend/src/domain/booking/pricing.ts`
- `packages/backend/src/domain/booking/rules.test.ts`
- `packages/backend/src/domain/booking/rules.ts`
