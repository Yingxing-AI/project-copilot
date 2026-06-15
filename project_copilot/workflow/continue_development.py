from __future__ import annotations

from project_copilot.analyzer import analyze_project
from project_copilot.memory import MemoryStore
from project_copilot.workflow.types import WorkflowContext
from project_copilot.workflow.utils import format_next_steps


def run(context: WorkflowContext) -> str:
    MemoryStore(context.root).ensure()
    analysis = analyze_project(context.root)
    return "\n".join(
        [
            "已读取项目记忆。",
            f"当前阶段：{analysis.stage}",
            format_next_steps(analysis.next_steps),
            "建议先确认是否实施第一项任务。",
        ]
    )
