from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitStatus:
    available: bool
    initialized: bool
    branch: str | None
    dirty_files: list[str]
    last_commit: str | None


def _run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def init_git_if_needed(root: Path) -> bool:
    exact_root = _run_git(root, ["rev-parse", "--show-toplevel"])
    if exact_root.returncode == 0 and Path(exact_root.stdout.strip()).resolve() == root.resolve():
        return False
    result = _run_git(root, ["init"])
    return result.returncode == 0


def inspect_git(root: Path) -> GitStatus:
    available_result = _run_git(root, ["--version"])
    if available_result.returncode != 0:
        return GitStatus(False, False, None, [], None)

    inside_result = _run_git(root, ["rev-parse", "--is-inside-work-tree"])
    initialized = inside_result.returncode == 0 and inside_result.stdout.strip() == "true"
    if not initialized:
        return GitStatus(True, False, None, [], None)

    branch_result = _run_git(root, ["branch", "--show-current"])
    status_result = _run_git(root, ["status", "--short", "--", "."])
    commit_result = _run_git(root, ["log", "-1", "--pretty=%h %s"])

    return GitStatus(
        available=True,
        initialized=True,
        branch=branch_result.stdout.strip() or None,
        dirty_files=[line.strip() for line in status_result.stdout.splitlines() if line.strip()],
        last_commit=commit_result.stdout.strip() if commit_result.returncode == 0 else None,
    )
