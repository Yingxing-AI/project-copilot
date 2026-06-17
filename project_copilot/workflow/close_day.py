from __future__ import annotations

from datetime import datetime

from project_copilot.analyzer import analyze_project
from project_copilot.memory import MemoryStore
from project_copilot.workflow.sync_project_state import sync_project_state
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    memory = MemoryStore(context.root)
    memory.ensure()
    analysis = analyze_project(context.root)
    now = datetime.now()
    _append_worklog(memory, now.strftime("%Y-%m-%d %H:%M"), analysis.stage, analysis.health_score)
    sync = sync_project_state(context.root)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已结束今日工作。",
        summary="已更新项目状态、工作日志、路线图和项目协作记忆。",
        details={
            "当前开发阶段": analysis.stage,
            "更新文件": [".ai/WORKLOG.md", *sync.updated_files],
            "当前风险": analysis.risks,
        },
        next_steps=["次日继续时，先恢复当前上下文，再根据实际进展决定下一步。"],
    )


def _append_worklog(memory: MemoryStore, stamp: str, stage: str, health_score: int) -> None:
    path = memory.ai_dir / "WORKLOG.md"
    if not path.exists():
        path.write_text("# Worklog\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n## {stamp}\n\n")
        handle.write("- 已更新项目状态。\n")
        handle.write(f"- 当前阶段：{stage}\n")
        handle.write(f"- 项目健康度：{health_score}/100\n")
