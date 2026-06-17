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
    decisions = _recent_lines(memory.read("DECISIONS.md"), limit=5) or ["暂无关键决策"]

    summary = "\n".join(
        [
            "项目健康度",
            f"{analysis.health_score}/100",
            "",
            "已完成",
            *[f"- {item}" for item in completed],
            "",
            "当前风险",
            *[f"- {item}" for item in risks],
            "",
            "下一阶段",
            *[f"- {item}" for item in analysis.next_steps[:4]],
            "",
            "关键决策",
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
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    path = memory.ai_dir / "history" / f"review-{stamp}.md"
    path.write_text(f"# Review {stamp}\n\n{summary}\n", encoding="utf-8")
    memory.append_memory("完成一次项目复盘。")


def _recent_lines(text: str, limit: int) -> list[str]:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            lines.append(stripped[2:])
        elif stripped.startswith("## ") and "暂无" not in stripped:
            lines.append(stripped[3:])
    return lines[-limit:]
