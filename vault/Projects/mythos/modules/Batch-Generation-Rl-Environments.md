---
cortex-generated: true
title: batch-generation-rl-environments
tags: [module]
---

# Batch generation & RL environments

**Project:** [[mythos]] | **Confidence:** inferred | **verified@** `15e9faf0b5db`
**Owns:** `environments/,batch_runner.py,trajectory_compressor.py,toolset_distributions.py,rl_cli.py,mini_swe_runner.py`

purpose: trajectory generation/compression and Atropos RL training envs (research heritage from Hermes).
path_prefixes: environments/, batch_runner.py, trajectory_compressor.py, toolset_distributions.py, rl_cli.py, mini_swe_runner.py
key_files: environments/hermes_base_env.py, agentic_opd_env.py, web_research_env.py
entrypoints: rl_cli.py; [rl] extra (atroposlib/tinker pinned git SHAs)
responsibilities: parallel batch runs, tool-call parsers, benchmark harnesses (yc-bench extra)
pitfalls: doc 06 originally mandated REMOVING these as Nous data-collection pipelines; they survive as opt-in research tooling [inferred — kept but decoupled from product defaults]
confidence: medium

## Files (40+)

- `batch_runner.py`
- `environments/__init__.py`
- `environments/agent_loop.py`
- `environments/agentic_opd_env.py`
- `environments/benchmarks/__init__.py`
- `environments/benchmarks/tblite/__init__.py`
- `environments/benchmarks/tblite/tblite_env.py`
- `environments/benchmarks/terminalbench_2/__init__.py`
- `environments/benchmarks/terminalbench_2/terminalbench2_env.py`
- `environments/benchmarks/yc_bench/__init__.py`
- `environments/benchmarks/yc_bench/yc_bench_env.py`
- `environments/hermes_base_env.py`
- `environments/hermes_swe_env/__init__.py`
- `environments/hermes_swe_env/hermes_swe_env.py`
- `environments/patches.py`
- `environments/terminal_test_env/__init__.py`
- `environments/terminal_test_env/terminal_test_env.py`
- `environments/tool_call_parsers/__init__.py`
- `environments/tool_call_parsers/deepseek_v3_1_parser.py`
- `environments/tool_call_parsers/deepseek_v3_parser.py`
- `environments/tool_call_parsers/glm45_parser.py`
- `environments/tool_call_parsers/glm47_parser.py`
- `environments/tool_call_parsers/hermes_parser.py`
- `environments/tool_call_parsers/kimi_k2_parser.py`
- `environments/tool_call_parsers/llama_parser.py`
