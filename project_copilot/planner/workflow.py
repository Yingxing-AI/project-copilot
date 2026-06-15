from __future__ import annotations

from pathlib import Path

from project_copilot.workflow import run_text_workflow


def run_workflow(root: Path, text: str) -> str:
    return run_text_workflow(root, text)
