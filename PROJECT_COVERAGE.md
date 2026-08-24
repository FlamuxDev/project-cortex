# Project Coverage

**Generated:** 2026-08-25 · source of truth: `cortex projects` / `cortex status <p>`

| Project | Kind | Files | Symbols | Modules | Flows | APIs | DB ents | Tests | Memories | Decisions | Git |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| campify | monorepo (pnpm) | 298 | 1,347 | 20 | 8 | 70 | 109 | 71 | 28+ | 14 | ✓ |
| chat-agent-saas | monorepo (npm+turbo) | 957 | 4,589 | 13 | 5 | 550 | 135 | 161 | 21 | 10 | ✓ |
| cvm | monorepo (pnpm) | 432 | 2,761 | 24 | 8 | 539 | 298 | 50 | 32 | 13 | ✓ |
| faraj (farj-portfolio) | app | 48 | 82 | 5 | 3 | — | — | — | 13 | 6 | ✗ no git |
| iscc-testing | Odoo suite | 80 | 207 | 9 | 3 | — | — | 3 | 17 | 6 | ✓ |
| luma | multi-service JS | 477 | 1,324 | 7 | 4 | 362 | 65 | 146 | 15 | 9 | ✓ |
| mawid-ai | monorepo (pnpm+turbo) | 379 | 1,208 | 16 | 7 | 27 | 92 | 25 | 24 | 10 | ✓ |
| mushagil | monorepo (pnpm+turbo) | 572 | 2,227 | 11 | 9 | 162 | 90 | 133 | 19 | 13 | ✓ |
| mythos | python agent platform | 2,022 | 47,934 | 15 | 6 | 144 | 33 | 1,090 | 23 | 9 | ✓ |
| sham-v2 | node agent app | 71 | 516 | 7 | 4 | 38 | 93 | 12 | 15 | 7 | ✓ |
| shamsieh | Odoo customization | 297 | 1,564 | 10 | 4 | 4 | — | 23 | 18 | 6 | ✓ |
| telvora | Go + TS monorepo | 758 | 3,467 | 13 | 7 | 301 | 104 | 197 | 21 | 8 | ✓ |
| test-ai | python bot backend | 95 | 1,055 | 10 | 5 | 36 | 97 | 29 | 18 | 7 | ✓ |
| umbrellaprime | next.js static | 59 | 89 | 6 | 4 | — | — | 4 | 14 | 8 | ✓ |
| **Total** | 14 projects | **6,545** | **68,370** | **166** | **77** | **~2,230** | **1,116** | **1,944** | **288 (+10 global)** | **124** |

Excluded deliberately: `pems/` (SSH private keys — never indexed).

## Quality dashboard

| Signal | Status |
|---|---|
| Index freshness at build time | all 14 FRESH vs HEAD (several repos carry dirty worktrees — flagged live in packets) |
| Module coverage from delegate reports | 166 modules across 14/14 projects |
| Test mapping coverage | import-derived targets for all test files that import source |
| Retrieval evaluation | 20/20 (see RETRIEVAL_EVALUATION.md) |
| Hallucination audit | 45 verified / 4 incorrect / 3 obsolete / 2 unsupported, 0 fabricated (HALLUCINATION_AUDIT.md) |
| Adversarial audit | pre-fix 7 PASS/9 PARTIAL/9 FAIL → cross-project, guardrail & freshness fixes landed; details in ADVERSARIAL_AUDIT.md |
| Vault notes generated | ~200 Obsidian pages (regenerable, never clobbers human edits) |

Regenerate any time:

```bash
cortex update                 # refresh code indexes incrementally
.venv/bin/python src/cortex/vault.py
```
