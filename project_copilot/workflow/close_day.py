from __future__ import annotations

from datetime import datetime

from project_copilot.analyzer import analyze_project
from project_copilot.memory import MemoryStore
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    memory = MemoryStore(context.root)
    memory.ensure()
    analysis = analyze_project(context.root)
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    status = "\n".join(
        [
            "# Status",
            "",
            f"更新日期：{today}",
            f"当前阶段：{analysis.stage}",
            "",
            "已完成功能：",
            *[f"- {item}" for item in analysis.completed],
            "",
            "下一步任务：",
            *[f"- {item}" for item in analysis.next_steps],
            "",
        ]
    )
    memory.update_status(status)
    _append_worklog(memory, now.strftime("%Y-%m-%d %H:%M"), analysis.next_steps)
    memory.append_memory("结束工作并更新项目状态。")
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已结束今日工作。",
        summary="已更新项目状态、.ai/WORKLOG.md 和 .ai/MEMORY.md。",
        details={
            "当前开发阶段": analysis.stage,
            "更新文件": [".ai/STATUS.md", ".ai/WORKLOG.md", ".ai/MEMORY.md"],
            "当前风险": analysis.risks,
        },
        next_steps=analysis.next_steps,
    )


def _append_worklog(memory: MemoryStore, stamp: str, next_steps: list[str]) -> None:
    path = memory.ai_dir / "WORKLOG.md"
    if not path.exists():
        path.write_text("# Worklog\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n## {stamp}\n\n")
        handle.write("- 已更新项目状态。\n")
        for step in next_steps:
            handle.write(f"- 下一步：{step}\n")
