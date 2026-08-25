"""Mixed Arabic/English engineering retrieval evaluation.

8 realistic developer phrasings (Levantine + English code terms) with curated
ground truth verified to exist in the target repos. PASS = ground truth in
the packet at budget 3000.
"""
import json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from cortex.db import connect            # noqa: E402
from cortex.contextpack import context   # noqa: E402

CASES = [
    ("mawid-ai", "وين نظام الحجوزات؟", ["booking"]),
    ("sham-v2", "وين الشي الي يمنع duplicate requests؟", ["workflow-engine", "idempotency"]),
    ("mushagil", "عدل knowledge base validation", ["knowledge"]),
    ("campify", "صلح validation حق campaign", ["campaign"]),
    ("cvm", "وين tenant isolation؟", ["tenant"]),
    ("chat-agent-saas", "غير ال authentication flow تبع login", ["auth"]),
    ("telvora", "وين ال worker الي يسوي embedding؟", ["worker"]),
    ("test-ai", "عدل webhook handler حق whatsapp", ["webhook"]),
]


def main():
    con = connect()
    passed = 0
    details = []
    for pid, task, truths in CASES:
        r = context(con, task, project_id=pid, budget=3000)
        packet = r.get("packet") or ""
        ok = any(t in packet for t in truths)
        passed += ok
        details.append({"project": pid, "task": task, "pass": ok,
                        "tokens": r.get("tokens_est"),
                        "evidence_warning": "EVIDENCE WARNING" in packet})
        print(f"[{'PASS' if ok else 'FAIL'}] {pid:14} {task}")
    print(f"\nArabic/mixed retrieval — {passed}/{len(CASES)}")
    out = pathlib.Path(__file__).resolve().parents[1] / "ARABIC_EVALUATION.json"
    out.write_text(json.dumps(details, ensure_ascii=False, indent=1))
    print(f"details -> {out}")


if __name__ == "__main__":
    main()
