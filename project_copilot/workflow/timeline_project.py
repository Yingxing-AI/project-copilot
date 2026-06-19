from __future__ import annotations

import re
from pathlib import Path

from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    ai_dir = context.root / ".ai"
    adr_items = _adr_items(ai_dir / "adr", limit=5)
    history_items = _history_items(ai_dir / "history", limit=5)
    session_items = _session_archive_items(ai_dir / "sessions" / "archive", limit=5)
    legacy_decisions = _legacy_decision_items(ai_dir / "DECISIONS.md", limit=3) if not adr_items else []

    summary = "\n".join(
        [
            "ADR 决策：",
            *[f"- {item}" for item in adr_items or legacy_decisions or ["暂无 ADR。"]],
            "",
            "里程碑归档：",
            *[f"- {item}" for item in history_items or ["暂无 history 里程碑。"]],
            "",
            "Session Archive：",
            *[f"- {item}" for item in session_items or ["暂无已归档 Session。"]],
        ]
    )
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="项目决策与里程碑时间轴",
        summary=summary,
        details={
            "来源优先级": "adr/ → history/ → sessions/archive/；旧 DECISIONS 仅作无 ADR 时的兼容回退。",
        },
        next_steps=["结束工作时把三个月后仍重要的候选事件沉淀为 ADR、history 或 knowledge。"],
    )


def _adr_items(adr_dir: Path, limit: int) -> list[str]:
    try:
        paths = sorted(path for path in adr_dir.glob("*.md") if re.match(r"^\d{4}-", path.name))
    except OSError:
        return []
    items: list[str] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        title = _first_heading(text) or path.stem
        date = _field(text, "日期") or "日期待记录"
        status = _field(text, "状态") or "状态待记录"
        items.append(f"{date} [{status}] {title}")
    return items[-limit:]


def _history_items(history_dir: Path, limit: int) -> list[str]:
    try:
        paths = sorted(path for path in history_dir.glob("*.md") if path.is_file())
    except OSError:
        return []
    items: list[str] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for heading in re.findall(r"^##\s+(.+)$", text, flags=re.MULTILINE):
            items.append(f"{path.name}: {heading.strip()}")
    return items[-limit:]


def _session_archive_items(archive_dir: Path, limit: int) -> list[str]:
    try:
        paths = sorted(path for path in archive_dir.iterdir() if path.is_file() and not path.name.startswith("."))
    except OSError:
        return []
    items: list[str] = []
    for path in paths[-limit:]:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        heading = _first_heading(text)
        items.append(f"{path.name}: {heading or 'Session archive'}")
    return items


def _legacy_decision_items(path: Path, limit: int) -> list[str]:
    try:
        if not path.exists():
            return []
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- 决策："):
            items.append(stripped.removeprefix("- 决策：").strip())
        elif stripped.startswith("决策："):
            items.append(stripped.removeprefix("决策：").strip())
    return items[-limit:]


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped.removeprefix("# ").strip()
    return ""


def _field(text: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}：(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""
