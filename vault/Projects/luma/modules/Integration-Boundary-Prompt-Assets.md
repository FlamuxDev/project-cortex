---
cortex-generated: true
title: integration-boundary-prompt-assets
tags: [module]
---

# integration boundary + prompt assets

**Project:** [[luma]] | **Confidence:** inferred | **verified@** `da7bced5651b`
**Owns:** `ai-engine/prompts/,ai-engine/contracts/,backend-luma/contracts/,ai-engine/docs/`

purpose: machine-readable worker/backend contract and versioned prompt blocks/checks/drafts for the agent council.
path_prefixes: ai-engine/prompts/, ai-engine/contracts/, backend-luma/contracts/, ai-engine/docs/
key_files: contracts/worker-backend-api.v1.yaml, contracts/worker-schema-contract.v1.json, prompts/README.md, prompts/blocks/, docs/worker-contract.md, docs/architecture.md
entrypoints: contract check via npm run test:contract
responsibilities: cross-team change review requirement; provenance docs (docs/provenance.md); runbooks + capacity benchmark docs.
invariants: contract changes require review by both owners (worker-contract.md).
confidence: high

