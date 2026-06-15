from __future__ import annotations

from datetime import datetime

from project_copilot.analyzer import analyze_project
from project_copilot.memory import MemoryStore
from project_copilot.workflow.check_project import run as check_project
from project_copilot.workflow.types import WorkflowContext


def run(context: WorkflowContext) -> str:
    memory = MemoryStore(context.root)
    analysis = analyze_project(context.root)
    today = datetime.now().strftime("%Y-%m-%d")
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
    memory.append_memory("结束工作并更新项目状态。")
    return "已更新项目状态、项目记忆和工作总结。\n" + check_project(context)
