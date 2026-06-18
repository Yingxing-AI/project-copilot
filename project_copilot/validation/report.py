from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from project_copilot.validation.snapshot import (
    ValidationSnapshot,
    collect_validation_snapshot,
    export_validation_snapshot,
    load_validation_snapshot,
)


@dataclass(frozen=True)
class ValidationRecord:
    project_name: str
    started_at: str
    status: str
    usage_days: int | None = None
    worklog_count: int | None = None
    decision_count: int | None = None
    knowledge_count: int | None = None
    source: str = "case_study"
    source_path: str | None = None


def refresh_validation_report(root: Path) -> tuple[Path, list[ValidationRecord]]:
    snapshot = collect_validation_snapshot(root)
    if snapshot:
        export_validation_snapshot(root, snapshot)
    records = build_validation_records(root)
    path = root / "docs" / "validation-report.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_validation_report(records), encoding="utf-8")
    return path, records


def build_validation_records(root: Path) -> list[ValidationRecord]:
    records: dict[str, ValidationRecord] = {}

    case_study_dir = root / "docs" / "case-studies"
    if case_study_dir.is_dir():
        for path in sorted(case_study_dir.glob("*.md")):
            if path.name == "template.md":
                continue
            record = load_case_study_record(path)
            if record:
                records[record.project_name] = record

    for project_root in iter_validation_project_roots(root):
        snapshot_path = project_root / ".ai" / "validation.json"
        if _has_live_memory_files(project_root):
            snapshot = collect_validation_snapshot(project_root)
            if snapshot and snapshot.project_name:
                records[snapshot.project_name] = _snapshot_to_record(snapshot, snapshot_path)
                continue
        if not _safe_exists(snapshot_path):
            continue
        snapshot = load_validation_snapshot(snapshot_path)
        if not snapshot or not snapshot.project_name:
            continue
        records[snapshot.project_name] = _snapshot_to_record(snapshot, snapshot_path)

    return sorted(records.values(), key=lambda record: (record.started_at or "9999-99-99", record.project_name))


def _has_live_memory_files(root: Path) -> bool:
    ai_dir = root / ".ai"
    for name in (
        "PROJECT_CONTEXT.md",
        "STATUS.md",
        "MEMORY.md",
        "HYPOTHESES.md",
        "ROADMAP.md",
        "DECISIONS.md",
        "WORKLOG.md",
        "KNOWLEDGE.md",
    ):
        path = ai_dir / name
        try:
            if path.exists():
                return True
        except OSError:
            continue
    return False


def render_validation_report(records: list[ValidationRecord]) -> str:
    total_worklogs = sum(record.worklog_count or 0 for record in records)
    total_decisions = sum(record.decision_count or 0 for record in records)
    total_knowledge = sum(record.knowledge_count or 0 for record in records)

    lines = [
        "# Validation Report",
        "",
        "验证目标：",
        "",
        "验证 Project Copilot 是否能持续维护项目记忆。",
        "",
        "---",
        "",
        "## 项目列表",
        "",
        "| 项目名称 | 开始时间 | 使用天数 | 工作日志 | 决策 | 知识沉淀 | 状态 |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for record in records:
        lines.append(
            "| {name} | {started} | {days} | {worklogs} | {decisions} | {knowledge} | {status} |".format(
                name=record.project_name,
                started=record.started_at or "待记录",
                days=_fmt_int(record.usage_days),
                worklogs=_fmt_int(record.worklog_count),
                decisions=_fmt_int(record.decision_count),
                knowledge=_fmt_int(record.knowledge_count),
                status=record.status or "待记录",
            )
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "## 统计汇总",
            "",
            f"总项目数：{len(records)}",
            "",
            f"总工作日志：{total_worklogs}",
            "",
            f"总决策：{total_decisions}",
            "",
            f"总知识沉淀：{total_knowledge}",
            "",
            "---",
            "",
            "## 关键发现",
            "",
            "- Project Copilot 已能在真实项目中形成可审阅的 `.ai/` 项目记忆。",
            "- 工作日志、决策和知识沉淀可以作为多项目验证的基础指标。",
        ]
    )
    if any(record.source == "snapshot" for record in records):
        lines.append("- 验证汇总现在可以从 `.ai/validation.json` 快照自动刷新，不再依赖人工抄写统计值。")
    lines.extend(
        [
            "- 验证体系应优先观察项目记忆是否长期可读、可维护、可复盘，而不是继续新增功能。",
            "",
            "---",
            "",
            "## 下一阶段计划",
            "",
            "- 纳入更多真实项目。",
            "- 每个项目使用统一 case study 模板记录。",
            "- 每周更新统计汇总。",
            "- 对比不同项目中的工作日志、决策和知识沉淀质量。",
            "",
        ]
    )
    return "\n".join(lines)


def load_case_study_record(path: Path) -> ValidationRecord | None:
    text = path.read_text(encoding="utf-8")
    project_name = _match(text, r"^项目名称：(.+)$")
    started_at = _match(text, r"^开始使用日期：(.+)$")
    status = _match(text, r"^当前状态：(.+)$")
    if not project_name:
        return None
    return ValidationRecord(
        project_name=project_name,
        started_at=started_at or "待记录",
        status=status or "待记录",
        usage_days=_parse_int(_match(text, r"^使用天数：(.+)$")),
        worklog_count=_parse_int(_match(text, r"^工作日志数量：(.+)$")),
        decision_count=_parse_int(_match(text, r"^决策数量：(.+)$")),
        knowledge_count=_parse_int(_match(text, r"^知识沉淀数量：(.+)$")),
        source="case_study",
        source_path=str(path),
    )


def _snapshot_to_record(snapshot: ValidationSnapshot, path: Path) -> ValidationRecord:
    return ValidationRecord(
        project_name=snapshot.project_name,
        started_at=snapshot.started_at or "待记录",
        status=snapshot.status or "待记录",
        usage_days=snapshot.usage_days,
        worklog_count=snapshot.worklog_count,
        decision_count=snapshot.decision_count,
        knowledge_count=snapshot.knowledge_count,
        source="snapshot",
        source_path=str(path),
    )


def iter_validation_project_roots(root: Path) -> list[Path]:
    candidates: list[Path] = [root]
    parent = root.parent
    if parent.exists():
        for candidate in parent.iterdir():
            try:
                if not candidate.is_dir():
                    continue
                candidates.append(candidate)
            except OSError:
                continue
    return candidates


def _match(text: str, pattern: str) -> str:
    match = re.search(pattern, text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _parse_int(value: str) -> int | None:
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _fmt_int(value: int | None) -> str:
    return str(value) if value is not None else "待记录"


def _safe_exists(path: Path) -> bool:
    try:
        return path.exists()
    except OSError:
        return False
