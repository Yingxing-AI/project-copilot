from __future__ import annotations

from project_copilot.memory import MemoryStore
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    memory = MemoryStore(context.root)
    memory.ensure()
    roadmap = memory.read("ROADMAP.md").strip()
    summary = roadmap if roadmap else "暂无路线图。"
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="项目路线图",
        summary=summary,
        next_steps=["如果新增需求不在路线图中，先运行“项目偏航检查”。"],
    )
