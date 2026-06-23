from __future__ import annotations

import re
from dataclasses import dataclass

from project_copilot.memory import MemoryStore
from project_copilot.validation.report import refresh_validation_report as refresh_validation_report_file
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


@dataclass(frozen=True)
class SessionEntry:
    category: str
    text: str


def run(context: WorkflowContext) -> WorkflowResult:
    memory = MemoryStore(context.root)
    current_text = memory.read_session_candidates()
    entries = _parse_entries(current_text)
    archive_content = _render_archive(entries)
    archive_path = memory.write_session_archive(archive_content)
    reset_path = memory.reset_session_candidates()
    validation_report_path, _ = refresh_validation_report_file(context.root)

    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已生成 Session Archive。",
        summary="已将当日候选事件归档到 Session Archive，重置当前会话缓冲区，并刷新 Validation 派生视图。",
        details={
            "归档文件": str(archive_path.relative_to(context.root)),
            "候选数量": len(entries),
            "重置缓冲区": str(reset_path.relative_to(context.root)),
            "验证汇总": str(validation_report_path.relative_to(context.root))
            if validation_report_path.is_relative_to(context.root)
            else str(validation_report_path),
        },
        next_steps=[
            "下一次开始工作会从 current.md 重新积累候选。",
            "Session Archive 只记录三个月后仍重要的开发上下文。",
        ],
    )


def _parse_entries(text: str) -> list[SessionEntry]:
    entries: list[SessionEntry] = []
    pattern = re.compile(r"^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} \[(.+?)\] (.+)$")
    for line in text.splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        entries.append(SessionEntry(category=match.group(1).strip(), text=match.group(2).strip()))
    return entries


def _render_archive(entries: list[SessionEntry]) -> str:
    groups = {
        "progress": [],
        "adr": [],
        "risk": [],
        "scope": [],
        "important": [],
    }
    for entry in entries:
        bucket = _bucket_for(entry)
        groups[bucket].append(entry.text)

    return "\n".join(
        [
            "## 今日关键进展",
            *_render_bullets(groups["progress"]),
            "",
            "## 新增或确认的 ADR",
            *_render_bullets(groups["adr"]),
            "",
            "## 风险变化",
            *_render_bullets(groups["risk"]),
            "",
            "## 范围变化",
            *_render_bullets(groups["scope"]),
            "",
            "## 重要候选事项",
            *_render_bullets(groups["important"]),
        ]
    )


def _render_bullets(items: list[str]) -> list[str]:
    if not items:
        return ["- 暂无。"]
    return [f"- {item}" for item in items]


def _bucket_for(entry: SessionEntry) -> str:
    category = entry.category.lower()
    text = entry.text.lower()
    if "adr" in category or "决策" in category:
        return "adr"
    if "risk" in category or "风险" in category or "风险" in text:
        return "risk"
    if "mile" in category or "里程碑" in category:
        return "progress"
    if "范围" in text or "mvp" in text or "scope" in text:
        return "scope"
    if "know" in category or "知识" in category:
        return "important"
    return "progress"
