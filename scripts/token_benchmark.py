"""Token-efficiency benchmark: baseline agent discovery vs cortex-assisted.

Methodology (honest, simulated policies over real tools):
- BASELINE: an agent with no brain explores using ripgrep. Policy: extract task
  keywords, `rg -l` each keyword (cumulative), then open candidate files
  (reading up to 150 lines each) until a ground-truth evidence file appears in
  results or candidates are exhausted. Cost = all bytes surfaced to the agent.
- CORTEX: one context packet at budget B, plus reading the top primary file.
  Cost = packet bytes + that file's read bytes.
Ground truth = curated evidence paths from the retrieval eval set.
"""
from __future__ import annotations
import pathlib, subprocess, sys, time, statistics

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cortex.db import connect
from cortex.contextpack import context
from cortex.search import keywords

CASES = [
    ("mushagil", "/home/aboud/Dev/Mushagil",
     "Fix duplicate knowledge-base document ingestion", ["knowledge.controller", "knowledge.service"]),
    ("campify", "/home/aboud/Dev/Campify",
     "Tenant isolation leaking rows between workspaces", ["db.ts", "tenant"]),
    ("cvm", "/home/aboud/Dev/CVM",
     "Where is the API route registration for analytics", ["analyticsRoutes"]),
    ("telvora", "/home/aboud/Dev/Telvora",
     "Fix webhook signature verification for telecom events", ["webhook.go"]),
    ("chat-agent-saas", "/home/aboud/Dev/chat-agent-saas",
     "Voice custom LLM bridge 404 every turn", ["voiceLlm"]),
    ("mawid-ai", "/home/aboud/Dev/Mawid-AI",
     "WhatsApp webhook dedupe fails for repeated messages", ["webhook"]),
]

BUDGET_TOKENS = 3000


def file_head_bytes(p: pathlib.Path, lines=150) -> int:
    try:
        with p.open("rb") as f:
            return sum(len(f.readline()) for _ in range(lines))
    except OSError:
        return 0


def baseline_cost(repo: str, task: str, truth: list[str]) -> tuple[int, bool]:
    """Simulated rg+read policy; returns (bytes consumed, found)."""
    cost = 0
    kws = keywords(task)[:6]
    seen: set[str] = set()
    candidates: list[str] = []
    for kw in kws:
        r = subprocess.run(["rg", "-li", "--max-count", "1", kw, ".",
                            "-g", "!node_modules", "-g", "!dist", "-g", "!.next"],
                           cwd=repo, capture_output=True, text=True, timeout=60)
        out = [l for l in r.stdout.splitlines() if l.strip()]
        cost += len(r.stdout) + len(kw)
        for line in out[:25]:
            if line not in seen:
                seen.add(line)
                candidates.append(line)
    found = False
    for rel in candidates[:30]:
        base = rel.removeprefix("./")
        hit = any(t.lower() in base.lower() for t in truth)
        cost += file_head_bytes(pathlib.Path(repo) / base)
        if hit:
            found = True
            break
    return cost, found


def cortex_cost(con, pid: str, task: str, truth: list[str]) -> tuple[int, bool, str]:
    r = context(con, task, project_id=pid, budget=BUDGET_TOKENS)
    packet = r.get("packet", "")
    cost = len(packet.encode())
    # first primary file read
    first_file = None
    for line in packet.splitlines():
        s = line.strip()
        if s and ("/" in s) and ("." in s.split("/")[-1]) and not s.startswith(("PROJECT", "PATH", "STACK")):
            first_file = s.split()[0]
            break
    if first_file:
        repo = {"mushagil": "/home/aboud/Dev/Mushagil", "campify": "/home/aboud/Dev/Campify",
                "cvm": "/home/aboud/Dev/CVM", "telvora": "/home/aboud/Dev/Telvora",
                "chat-agent-saas": "/home/aboud/Dev/chat-agent-saas", "mawid-ai": "/home/aboud/Dev/Mawid-AI"}[pid]
        cost += file_head_bytes(pathlib.Path(repo) / first_file)
    found = any(t.lower() in packet.lower() for t in truth)
    return cost, found, first_file or "-"


def main():
    con = connect()
    rows = []
    for pid, repo, task, truth in CASES:
        b_cost, b_found = baseline_cost(repo, task, truth)
        c_cost, c_found, first = cortex_cost(con, pid, task, truth)
        rows.append((pid, task, b_cost, c_cost, b_found, c_found))
        print(f"{pid:16} baseline={b_cost//1024:6}KB(found={b_found})  "
              f"cortex={c_cost//1024:5}KB(found={c_found})  reduction={100*(1-c_cost/max(b_cost,1)):.0f}%")
    b_med = statistics.median(r[2] for r in rows)
    c_med = statistics.median(r[3] for r in rows)
    print(f"\nmedian discovery cost: baseline {b_med/1024:.0f}KB vs cortex {c_med/1024:.0f}KB "
          f"-> {100*(1-c_med/b_med):.0f}% reduction")
    print("(bytes the agent must consume to locate the right implementation area)")


if __name__ == "__main__":
    main()
