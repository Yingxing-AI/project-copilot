from __future__ import annotations

from project_copilot.analyzer import analyze_project
from project_copilot.memory import MemoryStore
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    memory = MemoryStore(context.root)
    memory.ensure()
    status_text = memory.read("STATUS.md").strip()
    analysis = analyze_project(context.root)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已读取项目记忆。",
        summary=f"当前阶段：{analysis.stage}",
        details={
            "STATUS 摘要": _summarize_status(status_text),
        },
        next_steps=analysis.next_steps + ["确认后实施第一项任务。"],
    )


def _summarize_status(status_text: str) -> str:
    lines = [line.strip() for line in status_text.splitlines() if line.strip()]
    return "；".join(lines[:5]) if lines else "暂无 STATUS.md 内容。"
