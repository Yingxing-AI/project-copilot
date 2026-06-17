from __future__ import annotations

from project_copilot.analyzer import analyze_project
from project_copilot.memory import MemoryStore
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    memory = MemoryStore(context.root)
    memory.ensure()
    status_text = memory.read("STATUS.md").strip()
    hypotheses_text = memory.read("HYPOTHESES.md").strip()
    analysis = analyze_project(context.root)
    next_step = _resume_step(hypotheses_text)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已恢复当前上下文。",
        summary=f"当前阶段：{analysis.stage}",
        details={
            "STATUS 摘要": _summarize_status(status_text),
        "HYPOTHESES 摘要": _summarize_status(hypotheses_text) if hypotheses_text else "暂无 HYPOTHESES.md 内容。",
        },
        next_steps=[next_step],
    )


def _summarize_status(status_text: str) -> str:
    lines = [line.strip() for line in status_text.splitlines() if line.strip()]
    return "；".join(lines[:5]) if lines else "暂无 STATUS.md 内容。"


def _resume_step(hypotheses_text: str) -> str:
    if hypotheses_text.strip():
        return "优先确认未验证内容，再继续当前任务。"
    return "继续当前任务，不新增规划。"
