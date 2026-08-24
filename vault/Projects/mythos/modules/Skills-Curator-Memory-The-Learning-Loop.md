---
cortex-generated: true
title: skills-curator-memory-the-learning-loop
tags: [module]
---

# Skills, curator, memory (the "learning loop")

**Project:** [[mythos]] | **Confidence:** inferred | **verified@** `15e9faf0b5db`
**Owns:** `skills/,optional-skills/,agent/curator.py,agent/curator_backup.py,agent/memory_manager.py,agent/memory_provider.py,agent/skill_commands.py,tools/skill_*.py`

purpose: procedural memory — agent-created skills that self-improve; persistent curated memory; protected upstream asset.
path_prefixes: skills/, optional-skills/, agent/curator.py, agent/curator_backup.py, agent/memory_manager.py, agent/memory_provider.py, agent/skill_commands.py, tools/skill_*.py
key_files: agent/curator.py, tools/skill_usage.py (.usage.json sidecar), tools/skills_hub.py (agentskills.io standard + optional-skills installer)
entrypoints: slash `/<skill>` injected as user message (prompt-cache friendly); `safa curator <verb>`; `safa skills install`
responsibilities: skill creation/improvement, provenance tracking, tar.gz backups before runs, archive/restore/pin; memory provider orchestration (sync_turn/prefetch/shutdown/post_setup)
invariants: curator only touches created_by:"agent" skills; never deletes (max = archive to ~/.safa/skills/.archive/); pinned skills exempt everywhere; skill_manage delete refuses pinned
pitfalls: cron sessions pass skip_memory=True by design
confidence: high

## Files (40+)

- `agent/curator.py`
- `agent/curator_backup.py`
- `agent/memory_manager.py`
- `agent/memory_provider.py`
- `agent/skill_commands.py`
- `optional-skills/blockchain/base/scripts/base_client.py`
- `optional-skills/blockchain/solana/scripts/solana_client.py`
- `optional-skills/creative/kanban-video-orchestrator/scripts/bootstrap_pipeline.py`
- `optional-skills/creative/kanban-video-orchestrator/scripts/monitor.py`
- `optional-skills/creative/meme-generation/scripts/generate_meme.py`
- `optional-skills/finance/dcf-model/scripts/validate_dcf.py`
- `optional-skills/finance/excel-author/scripts/recalc.py`
- `optional-skills/health/fitness-nutrition/scripts/body_calc.py`
- `optional-skills/health/fitness-nutrition/scripts/nutrition_search.py`
- `optional-skills/mcp/fastmcp/scripts/scaffold_fastmcp.py`
- `optional-skills/mcp/fastmcp/templates/api_wrapper.py`
- `optional-skills/mcp/fastmcp/templates/database_server.py`
- `optional-skills/mcp/fastmcp/templates/file_processor.py`
- `optional-skills/migration/openclaw-migration/scripts/openclaw_to_mythos.py`
- `optional-skills/productivity/canvas/scripts/canvas_api.py`
- `optional-skills/productivity/memento-flashcards/scripts/memento_cards.py`
- `optional-skills/productivity/memento-flashcards/scripts/youtube_quiz.py`
- `optional-skills/productivity/telephony/scripts/telephony.py`
- `optional-skills/research/domain-intel/scripts/domain_intel.py`
- `optional-skills/research/drug-discovery/scripts/chembl_target.py`
