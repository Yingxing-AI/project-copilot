from __future__ import annotations

from datetime import datetime

from project_copilot.memory import MemoryStore
from project_copilot.secretary import inspect_secretary_status
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    memory = MemoryStore(context.root)
    memory.ensure()
    status = inspect_secretary_status(context.root)
    analysis = status.analysis
    completed = analysis.completed[:6] or ["暂无明确完成项"]
    risks = status.reminders[:5] or ["暂无明显风险"]
    decisions = _recent_decisions(memory.read("DECISIONS.md"), limit=3) or ["暂无关键决策"]

    summary = "\n".join(
        [
            "项目健康度：",
            f"{analysis.health_score}/100",
            "",
            "已完成：",
            *[f"- {item}" for item in completed],
            "",
            "当前风险：",
            *[f"- {item}" for item in risks],
            "",
            "下一步：",
            *[f"- {item}" for item in analysis.next_steps[:4]],
            "",
            "关键决策：",
            *[f"- {item}" for item in decisions],
        ]
    )
    _archive_review(memory, summary)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="项目复盘",
        summary=summary,
        next_steps=["根据风险更新路线图。", "把重要取舍用“记录决策 ...”保存下来。"],
    )


def _archive_review(memory: MemoryStore, summary: str) -> None:
    now = datetime.now()
    stamp = now.strftime("%Y-%m-%d-%H%M")
    month = now.strftime("%Y-%m")
    path = memory.ai_dir / "history" / f"{month}.md"
    entry = f"## {stamp}\n\n{summary}\n"
    if path.exists():
        existing = path.read_text(encoding="utf-8").rstrip()
        path.write_text(f"{existing}\n\n{entry}", encoding="utf-8")
    else:
        path.write_text(f"# History {month}\n\n{entry}", encoding="utf-8")


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
