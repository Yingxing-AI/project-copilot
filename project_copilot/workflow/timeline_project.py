from __future__ import annotations

from project_copilot.memory import MemoryStore
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    memory = MemoryStore(context.root)
    memory.ensure()
    milestones = _recent_items(memory.read("MEMORY.md"), limit=5) or ["暂无里程碑。"]
    worklog_items = _recent_worklog_items(memory.read("WORKLOG.md"), limit=4) or ["暂无工作记录。"]
    decisions = _recent_decisions(memory.read("DECISIONS.md"), limit=3) or ["暂无关键决策。"]
    summary = "\n".join(
        [
            "最近里程碑：",
            *[f"- {item}" for item in milestones],
            "",
            "近期工作：",
            *[f"- {item}" for item in worklog_items],
            "",
            "关键决策：",
            *[f"- {item}" for item in decisions],
        ]
    )
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="项目时间轴",
        summary=summary,
        next_steps=["结束工作时继续记录当天进展。", "完成阶段节点后运行“项目复盘”。"],
    )


def _recent_items(text: str, limit: int) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:])
    return items[-limit:]


def _recent_worklog_items(text: str, limit: int) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and "下一步" not in stripped:
            items.append(stripped[2:])
    return items[-limit:]


def _recent_decisions(text: str, limit: int) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []

    def flush() -> None:
        nonlocal current
        if not current:
            return
        decision = ""
        for line in current:
            stripped = line.strip()
            if stripped.startswith("- 决策："):
                decision = stripped.removeprefix("- 决策：").strip()
                break
        if decision:
            blocks.append(decision)
        current = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            flush()
            current = [line]
            continue
        if current:
            current.append(line)
    flush()
    return blocks[-limit:]
