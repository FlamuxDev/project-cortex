"""Install the bundled Project Cortex skill into agent discovery paths."""
from __future__ import annotations

from importlib import resources
import os
import pathlib
import tempfile


SKILL_NAME = "project-cortex"
_RESOURCE_FILES = ("SKILL.md", "agents/openai.yaml")


def _bundled_files() -> dict[str, bytes]:
    root = resources.files("cortex").joinpath("skills", SKILL_NAME)
    return {name: root.joinpath(*name.split("/")).read_bytes()
            for name in _RESOURCE_FILES}


def skill_destinations(
    scope: str = "user",
    *,
    home: pathlib.Path | None = None,
    project_root: pathlib.Path | None = None,
) -> list[pathlib.Path]:
    """Return portable and Claude-compatible skill destinations."""
    if scope == "user":
        base = pathlib.Path.home() if home is None else pathlib.Path(home)
    elif scope == "project":
        base = pathlib.Path.cwd() if project_root is None else pathlib.Path(project_root)
    else:
        raise ValueError("scope must be 'user' or 'project'")
    return [
        base / ".agents" / "skills" / SKILL_NAME,
        base / ".claude" / "skills" / SKILL_NAME,
    ]


def _atomic_write(path: pathlib.Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_name = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.",
                                         delete=False) as tmp:
            tmp.write(data)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_name = tmp.name
        pathlib.Path(tmp_name).replace(path)
    finally:
        if tmp_name:
            pathlib.Path(tmp_name).unlink(missing_ok=True)


def install_agent_skill(
    scope: str = "user",
    *,
    force: bool = False,
    home: pathlib.Path | None = None,
    project_root: pathlib.Path | None = None,
) -> list[dict[str, str]]:
    """Install the skill without overwriting local edits unless forced.

    ``~/.agents/skills`` is shared by Codex, Cursor, and OpenCode. Claude Code
    uses ``~/.claude/skills``, so the same portable skill is installed there as
    well. Project scope uses the equivalent paths under the selected repo.
    """
    bundled = _bundled_files()
    results: list[dict[str, str]] = []
    for destination in skill_destinations(
        scope, home=home, project_root=project_root
    ):
        existing = {
            name: destination.joinpath(*name.split("/")).read_bytes()
            for name in _RESOURCE_FILES
            if destination.joinpath(*name.split("/")).is_file()
        }
        conflict = any(data != bundled[name] for name, data in existing.items())
        changed = conflict or len(existing) != len(bundled)
        if conflict and not force:
            results.append({"path": str(destination), "status": "conflict"})
            continue
        if existing and changed:
            status = "updated"
        elif existing:
            status = "unchanged"
        else:
            status = "installed"
        if status != "unchanged":
            for name, data in bundled.items():
                _atomic_write(destination.joinpath(*name.split("/")), data)
        results.append({"path": str(destination), "status": status})
    return results
