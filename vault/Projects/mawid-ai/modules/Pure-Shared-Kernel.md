---
cortex-generated: true
title: pure-shared-kernel
tags: [module]
---

# Pure shared kernel

**Project:** [[mawid-ai]] | **Confidence:** inferred | **verified@** `1019517dfd75`
**Owns:** `packages/core/src/kernel/`

purpose: deterministic date/timezone/booking-rule logic; zero intra-repo imports (true leaf).
path_prefixes: packages/core/src/kernel/
key_files: datetime.ts (Arabic date parse, `afternoonWallClockGuess` 02:30→14:30), timezone.ts (`formatSlotLabel` — must use discrete Intl options, never weekday+dateStyle mix which throws), booking-rules.ts (`BookingRules`/`mergeBookingRules`/`effectiveBookingRules`), scheduling.ts (`buildSchedulingContext` calendar block for prompts), catalog.ts
entrypoints: library only
responsibilities: wall-clock↔UTC conversion, slot label formatting, rule merging, prompt calendar
invariants: no imports outside kernel; all date math flows through here, never ad-hoc `new Date()` arithmetic in callers
pitfalls: Intl option mixing throws; Arabic-Indic digits need `tabular-nums` (Plex Mono can't render them)
confidence: high

## Files (7+)

- `packages/core/src/kernel/booking-rules.ts`
- `packages/core/src/kernel/catalog.ts`
- `packages/core/src/kernel/datetime.test.ts`
- `packages/core/src/kernel/datetime.ts`
- `packages/core/src/kernel/scheduling.ts`
- `packages/core/src/kernel/timezone.test.ts`
- `packages/core/src/kernel/timezone.ts`
