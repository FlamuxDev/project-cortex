"""Retrieval evaluation runner.

Each question has ground-truth evidence substrings (file paths) that MUST appear
in a good context packet. Score = fraction of packets containing any/all targets.
"""
from __future__ import annotations
import json, pathlib, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cortex.db import connect
from cortex.contextpack import context, impact

QUESTIONS = [
    # project, task, at-least-one-of evidence substrings
    ("mushagil", "Fix duplicate knowledge-base document ingestion",
     ["knowledge.controller", "knowledge.service", "KnowledgeScreen"]),
    ("mushagil", "Change publication snapshot behavior for knowledge entries",
     ["publication", "knowledge"]),
    ("campify", "Tenant isolation is leaking rows between workspaces",
     ["db.ts", "rls", "tenant"]),
    ("campify", "Campaign launch flow fails after consent check",
     ["campaign", "consent"]),
    ("cvm", "Where is the API route registration for analytics?",
     ["analyticsRoutes", "apps/api/src/app.ts", "register"]),
    ("cvm", "Add a new facade-gated domain module to the API",
     ["facade", "app.ts", "wiring"]),
    ("telvora", "Fix webhook signature verification for telecom events",
     ["webhook.go", "ingestion"]),
    ("telvora", "Modify the real-time decision engine scoring",
     ["decision", "scoring", "realtime"]),
    ("chat-agent-saas", "Voice call custom LLM bridge returns 404 every turn",
     ["voiceLlm", "voice"]),
    ("chat-agent-saas", "Odoo report export bypasses chat authorization - fix it",
     ["odoo", "report", "export"]),
    ("mawid-ai", "WhatsApp webhook dedupe fails for repeated messages",
     ["webhook", "dedupe"]),
    ("mawid-ai", "Gemini agent loop integrity guard needs updating",
     ["agent", "gemini"]),
    ("luma", "Worker lease generation token collision on fenced queue",
     ["worker", "lease", "queue"]),
    ("sham-v2", "SQL guard rejects valid Arabic question about fees",
     ["guard", "sql", "agent"]),
    ("test-ai", "Nightly S3 restore job is failing",
     ["restore", "backup", "s3"]),
    ("shamsieh", "Fingerprint device sync from Hikvision bridge drops punches",
     ["hikvision", "fingerprint", "attendance"]),
    ("iscc-testing", "Payroll deduction calculation wrong for late violations",
     ["violation", "payroll", "deduction"]),
    ("mythos", "PowerPoint skill fails on generated OOXML",
     ["powerpoint", "ooxml", "skill"]),
    ("umbrellaprime", "Contact form does not submit on static export",
     ["contact", "form"]),
    ("faraj", "Portfolio project card hover animation broken",
     ["project", "card", "component"]),
]

IMPACT_CHECKS = [
    ("mushagil", "apps/api/src/business/knowledge.controller.ts"),
    ("campify", "apps/api/src/routes"),
    ("chat-agent-saas", "packages/api/src/jobs/workers/knowledge.worker.ts"),
]


def main():
    con = connect()
    results = []
    t_start = time.time()
    for pid, task, evidence in QUESTIONS:
        t0 = time.time()
        r = context(con, task, project_id=pid, budget=3000)
        packet = r.get("packet", "")
        hits = [e for e in evidence if e.lower() in packet.lower()]
        results.append({
            "project": pid, "task": task,
            "hit": len(hits) > 0,
            "hits": hits, "missed": [e for e in evidence if e not in hits],
            "tokens": r.get("tokens_est"), "secs": round(time.time() - t0, 2),
        })
    n_hit = sum(1 for r in results if r["hit"])
    print(f"RETRIEVAL EVALUATION — {n_hit}/{len(results)} packets contain ground-truth evidence "
          f"({100*n_hit/len(results):.0f}%)")
    for r in results:
        mark = "PASS" if r["hit"] else "FAIL"
        print(f"[{mark}] {r['project']:16} {r['task'][:60]:62} tokens={r['tokens']}")
        if not r["hit"]:
            print(f"       missed all of: {r['missed']}")
    lat = [r["secs"] for r in results]
    print(f"context latency p50={sorted(lat)[len(lat)//2]}s max={max(lat)}s total={time.time()-t_start:.1f}s")

    out = ROOT / "RETRIEVAL_EVALUATION.json"
    out.write_text(json.dumps({"score": f"{n_hit}/{len(results)}", "results": results}, indent=1))
    print("details ->", out)


if __name__ == "__main__":
    main()
