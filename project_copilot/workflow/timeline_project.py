from __future__ import annotations

from project_copilot.memory import MemoryStore
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    memory = MemoryStore(context.root)
    memory.ensure()
    events = _collect_events(memory.read("MEMORY.md"), memory.read("WORKLOG.md"))
    summary = "\n".join(f"- {event}" for event in events) if events else "- 暂无项目时间轴。"
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="项目时间轴",
        summary=summary,
        next_steps=["结束工作时继续记录当天进展。", "完成阶段节点后运行“项目复盘”。"],
    )


def _collect_events(memory_text: str, worklog_text: str) -> list[str]:
    events: list[str] = []
    for text in (memory_text, worklog_text):
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("- ") and "同步项目状态" not in stripped:
                events.append(stripped[2:])
            elif stripped.startswith("## ") and stripped != "## 决策记录":
                events.append(stripped[3:])
    return events[-12:]
