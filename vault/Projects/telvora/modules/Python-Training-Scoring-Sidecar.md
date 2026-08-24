---
cortex-generated: true
title: python-training-scoring-sidecar
tags: [module]
---

# Python training/scoring sidecar

**Project:** [[telvora]] | **Confidence:** verified | **verified@** `7423f040ed46`
**Owns:** `services/ml/app/*,services/ml/tests/*`

purpose: leakage-safe windowed training (churn classification, CLV regression, propensity/NBO with productCategory labels), scoring, driver explanations, segment metrics, artifact persistence
path_prefixes: services/ml/app/*, services/ml/tests/*
key_files: app/main.py (TrainRequest/ScoreRequest pydantic contracts), features.py, training.py, artifacts.py, db.py
entrypoints: uvicorn app.main:app :8090 (Makefile dev)
responsibilities: pure compute; returns metrics/artifactRef; Go owns all registry state
invariants: observationWindowDays+labelWindowDays must be provided together (model_validator main.py:77-81); artifact writes are local-dir stand-in for S3
pitfalls: Dockerfile needs libgomp1 for lightgbm (fixed 7423f04)
confidence: verified

