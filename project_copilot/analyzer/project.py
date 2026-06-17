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
    "AGENTS.md",
    ".ai/PROJECT_CONTEXT.md",
    ".ai/MEMORY.md",
    ".ai/ROADMAP.md",
    ".ai/STATUS.md",
    ".ai/DECISIONS.md",
    ".ai/WORKLOG.md",
    ".ai/KNOWLEDGE.md",
    ".ai/metrics.md",
]


def analyze_project(root: Path) -> ProjectAnalysis:
    git_status = inspect_git(root)
    completed = [path for path in REQUIRED_PATHS if (root / path).exists()]
    missing = [path for path in REQUIRED_PATHS if not (root / path).exists()]

    risks: list[str] = []
    if missing:
        risks.append("项目基础文件不完整。")
    if git_status.available and not git_status.initialized:
        risks.append("还没有保存进度记录。")
    if git_status.dirty_files:
        risks.append("有尚未保存的工作进展。")

    score = max(0, 100 - len(missing) * 7 - len(risks) * 8)
    if score >= 85:
        stage = "可持续开发"
    elif completed:
        stage = "MVP 搭建中"
    else:
        stage = "未初始化"

    next_steps = []
    if missing:
        next_steps.append("补齐项目档案和项目记忆。")
    if not git_status.initialized:
        next_steps.append("建立保存进度记录。")
    next_steps.append("根据路线图选择最高优先级任务继续开发。")

    return ProjectAnalysis(score, stage, completed, missing, risks, next_steps, git_status)
