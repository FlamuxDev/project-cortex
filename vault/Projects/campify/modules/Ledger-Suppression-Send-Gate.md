---
cortex-generated: true
title: ledger-suppression-send-gate
tags: [module]
---

# ledger, suppression, send gate

**Project:** [[campify]] | **Confidence:** verified | **verified@** `ad245fa6ef3d`
**Owns:** `packages/core/src/consent`

purpose: strict opt-in consent ledger + suppression list; THE gate every send passes.
path_prefixes: packages/core/src/consent
key_files: packages/core/src/consent/gate.ts, repository.ts; migrations 0003/0010/0012/0013
entrypoints: evaluateSendGate() (pure) called from checkSendAllowed() in dispatch; POST …/consent, POST …/suppressions
responsibilities: per-channel granted/withdrawn/pending/unknown; supersede trigger keeps one current row; suppression checked again at execution moment.
invariants: no bypass flag exists; relaxing policy is a legal/product decision, never code (ADR-0005); suppression evaluated BEFORE consent so unsubscribe beats a later re-grant; imported consent must carry explicit source+timestamp (import cannot fabricate).
pitfalls: consent_supersede's unique key was once occupiable by a foreign-tenant row (the ADR-0010 hole) leaving victims unable to record consent; writes serialized historically due to lock contention (commit 89b8ad2).
confidence: verified

