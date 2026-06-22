from __future__ import annotations

import re
from pathlib import Path

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
    decisions = _recent_adr_decisions(context.root / ".ai" / "adr", limit=3) or _recent_decisions(
        memory.read("DECISIONS.md"),
        limit=3,
    ) or ["暂无关键决策"]

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
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="项目复盘",
        summary=summary,
        next_steps=["这是只读复盘预览；需要归档时，请在收工确认中把它作为重大会话摘要写入。", "重要取舍应通过“记录决策 ...”进入 ADR。"],
    )


def _recent_adr_decisions(adr_dir: Path, limit: int) -> list[str]:
    try:
        paths = sorted(path for path in adr_dir.glob("*.md") if re.match(r"^\d{4}-", path.name))
    except OSError:
        return []

    decisions: list[str] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        title = _first_heading(text)
        if title.startswith("ADR "):
            title = title.split(": ", 1)[1] if ": " in title else title
        if title:
            decisions.append(title)
    return decisions[-limit:]


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
            if stripped.startswith("决策："):
                decision = stripped.removeprefix("决策：").strip()
                break
        if decision:
            blocks.append(decision)
        current = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## ") or stripped.startswith("日期："):
            flush()
            current = [line]
            continue
        if current:
            current.append(line)
    flush()
    return blocks[-limit:]


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped.removeprefix("# ").strip()
    return ""
