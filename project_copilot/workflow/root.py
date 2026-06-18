from __future__ import annotations

import subprocess
from pathlib import Path


def resolve_project_root(root: Path) -> Path:
    candidate = root.expanduser().resolve()
    if not candidate.exists():
        return candidate

    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=candidate,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip()).resolve()
    return candidate
