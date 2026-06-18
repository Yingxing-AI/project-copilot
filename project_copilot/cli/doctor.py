from __future__ import annotations

import platform
from pathlib import Path

from project_copilot.gitops import inspect_git


def render_doctor(root: Path) -> str:
    git = inspect_git(root)
    ai_dir = root / ".ai"
    core_memory_files = [
        "PROJECT_CONTEXT.md",
        "STATUS.md",
        "ROADMAP.md",
        "MEMORY.md",
        "HYPOTHESES.md",
        "DECISIONS.md",
        "WORKLOG.md",
        "KNOWLEDGE.md",
    ]
    auxiliary_files = ["metrics.md"]
    existing_core = [name for name in core_memory_files if (ai_dir / name).exists()]
    existing_auxiliary = [name for name in auxiliary_files if (ai_dir / name).exists()]

    lines = [
        "Project Copilot Doctor",
        f"Python：{platform.python_version()}",
        f"Git：{'available' if git.available else 'not found'}",
        f"当前目录：{root}",
        f".ai：{'ready' if ai_dir.is_dir() else 'missing'}",
    ]
    if git.initialized:
        lines.append(f"Git 分支：{git.branch or 'unknown'}")
    if existing_core:
        lines.append(".ai 核心记忆文件：" + ", ".join(existing_core))
    elif ai_dir.is_dir():
        lines.append(".ai 核心记忆文件：missing core files")

    if existing_auxiliary:
        lines.append(".ai 辅助文件：" + ", ".join(existing_auxiliary))

    if not ai_dir.is_dir():
        lines.append("建议：运行 `project-copilot 初始化项目` 或 `project-copilot 接管这个已有项目`。")
    return "\n".join(lines)
