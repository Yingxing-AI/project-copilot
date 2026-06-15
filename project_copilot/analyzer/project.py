from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from project_copilot.gitops import GitStatus, inspect_git


@dataclass(frozen=True)
class ProjectAnalysis:
    health_score: int
    stage: str
    completed: list[str]
    missing: list[str]
    risks: list[str]
    next_steps: list[str]
    git: GitStatus


REQUIRED_PATHS = [
    "README.md",
    "LICENSE",
    "AGENTS.md",
    ".ai/PROJECT_CONTEXT.md",
    ".ai/MEMORY.md",
    ".ai/ROADMAP.md",
    ".ai/STATUS.md",
    ".ai/DECISIONS.md",
    ".ai/WORKFLOW.md",
    ".ai/USER_PROFILE.md",
]


def analyze_project(root: Path) -> ProjectAnalysis:
    git_status = inspect_git(root)
    completed = [path for path in REQUIRED_PATHS if (root / path).exists()]
    missing = [path for path in REQUIRED_PATHS if not (root / path).exists()]

    risks: list[str] = []
    if missing:
        risks.append("项目基础文件不完整。")
    if git_status.available and not git_status.initialized:
        risks.append("Git 尚未初始化。")
    if git_status.dirty_files:
        risks.append("存在未提交变更。")

    score = max(0, 100 - len(missing) * 7 - len(risks) * 8)
    if score >= 85:
        stage = "可持续开发"
    elif completed:
        stage = "MVP 搭建中"
    else:
        stage = "未初始化"

    next_steps = []
    if missing:
        next_steps.append("补齐项目初始化文件和 .ai 项目记忆。")
    if not git_status.initialized:
        next_steps.append("初始化 Git 仓库。")
    next_steps.append("根据 ROADMAP 选择最高优先级任务继续开发。")

    return ProjectAnalysis(score, stage, completed, missing, risks, next_steps, git_status)
