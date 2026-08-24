---
cortex-generated: true
title: send-pipeline-retries-quiet-hours-provider-events
tags: [module]
---

# send pipeline, retries, quiet hours, provider events

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `packages/core/src/delivery,migrations 0021/0030/0031/0032`

purpose: turn a claimed message into a real send through every §13.3 control; ingest provider status.
path_prefixes: packages/core/src/delivery, migrations 0021/0030/0031/0032
key_files: packages/core/src/delivery/dispatch.ts, retry.ts, quietHours.ts, idempotency.ts, providerEventIngest.ts, repository.ts
entrypoints: worker tickDispatch → dispatch(); POST …/emergency-stops, GET …/messages, test-send/test-recipients/quiet-hours-override; POST /v1/providers/resend/webhook
responsibilities: order of gates: emergency stop → suppression → quiet hours → frequency cap → monthly quota → rate limit → resolve frozen content → personalize → port.send → classify transient/permanent → exponential backoff w/ jitter (MAX_ATTEMPTS); bounce/complaint ⇒ automatic suppression.
invariants: emergency stop and suppression re-checked AT EXECUTION (claim-time filtering insufficient); quiet hours before frequency cap (reservations commit immediately — don't spend caps on deferrals); quota lives HERE because campaigns, journey sends, and test sends converge on dispatch; idempotencyKey is `${message.id}:${attempt}` (retry may resend; duplicate claim collapses); quota-exceeded defers (allowance resets) while suppression fails permanently.
pitfalls: quiet-hours override set only by campaign:approve; test sends exempt from frequency/quota but NOT system rate limit; attribution anchor is messages.sent_at (commit cf88b83 fixed drift).
confidence: verified

