"""Git history mining: commits, co-change signals, durable lessons."""
from __future__ import annotations
import pathlib, re, subprocess

FIX_PAT = re.compile(r"^\s*(fix|bugfix|hotfix|revert|reapply)\b", re.I)


def _git(root: str, *args) -> str:
    r = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, timeout=120)
    return r.stdout if r.returncode == 0 else ""


def mine_history(root: str, since_sha: str | None = None) -> list[dict]:
    """Return [{sha,date,author,subject,category,files:[...]}]."""
    rng = f"{since_sha}..HEAD" if since_sha else "HEAD"
    log = _git(root, "log", "--name-only", "--pretty=format:%H%x00%aI%x00%an%x00%s", rng)
    commits = []
    cur = None
    for line in log.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x00")
        if len(parts) == 4:
            if cur:
                commits.append(cur)
            sha, date, author, subject = parts
            cat = ("fix" if FIX_PAT.match(subject) else
                   "feat" if subject.startswith(("feat", "add")) else
                   "refactor" if subject.startswith(("refactor", "clean")) else
                   "docs" if subject.startswith("docs") else
                   "chore")
            cur = {"sha": sha[:12], "date": date[:10], "author": author,
                   "subject": subject[:200], "category": cat, "files": []}
        elif cur is not None and not line.startswith("commit "):
            cur["files"].append(line.strip())
    if cur:
        commits.append(cur)
    return commits


def hotspots(commits: list[dict], top=30) -> dict[str, int]:
    counts: dict[str, int] = {}
    for c in commits:
        for f in c["files"]:
            counts[f] = counts.get(f, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1])[:top])


def cochange_pairs(commits: list[dict], min_count=4) -> list[tuple[str, str, int]]:
    pair_counts: dict[tuple[str, str], int] = {}
    for c in commits:
        fs = sorted({f for f in c["files"]})
        for i in range(len(fs)):
            for j in range(i + 1, min(i + 8, len(fs))):  # cap pairs per commit
                pair_counts[(fs[i], fs[j])] = pair_counts.get((fs[i], fs[j]), 0) + 1
    return [(a, b, n) for (a, b), n in pair_counts.items() if n >= min_count]
