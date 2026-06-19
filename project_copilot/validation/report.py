from __future__ import annotations

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
    adr_count: int | None = None
    session_archive_count: int | None = None
    active_candidate_count: int | None = None
    charter_present: bool | None = None
    roadmap_present: bool | None = None
    memory_health_status: str | None = None
    source: str = "snapshot"
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
        "PROJECT_CHARTER.md",
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
    for directory in (ai_dir / "adr", ai_dir / "sessions"):
        try:
            if directory.exists():
                return True
        except OSError:
            continue
    return False


def render_validation_report(records: list[ValidationRecord]) -> str:
    total_worklogs = sum(record.worklog_count or 0 for record in records)
    total_decisions = sum(record.decision_count or 0 for record in records)
    total_knowledge = sum(record.knowledge_count or 0 for record in records)
    total_adrs = sum(record.adr_count or 0 for record in records)
    total_session_archives = sum(record.session_archive_count or 0 for record in records)
    total_active_candidates = sum(record.active_candidate_count or 0 for record in records)
    charter_count = sum(1 for record in records if record.charter_present)
    roadmap_count = sum(1 for record in records if record.roadmap_present)

    lines = [
        "# Validation Report",
        "",
        "验证目标：",
        "",
        "验证 Project Copilot 是否能从真实 `.ai` 项目记忆中形成可复盘、可比较、可自动刷新的验证数据。",
        "",
        "---",
        "",
        "## 项目列表",
        "",
        "| 项目名称 | 开始时间 | 使用天数 | Charter | ADR | Session Archive | Active Candidates | Roadmap | 记忆状态 |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for record in records:
        lines.append(
            "| {name} | {started} | {days} | {charter} | {adrs} | {sessions} | {candidates} | {roadmap} | {memory_status} |".format(
                name=record.project_name,
                started=record.started_at or "待记录",
                days=_fmt_int(record.usage_days),
                charter=_fmt_bool(record.charter_present),
                adrs=_fmt_int(record.adr_count if record.adr_count is not None else record.decision_count),
                sessions=_fmt_int(record.session_archive_count),
                candidates=_fmt_int(record.active_candidate_count),
                roadmap=_fmt_bool(record.roadmap_present),
                memory_status=record.memory_health_status or record.status or "待记录",
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
            f"总 ADR：{total_adrs}",
            "",
            f"总 Session Archive：{total_session_archives}",
            "",
            f"总 Active Candidates：{total_active_candidates}",
            "",
            f"存在 Charter 的项目：{charter_count}",
            "",
            f"存在 Roadmap 的项目：{roadmap_count}",
            "",
            f"总知识沉淀：{total_knowledge}",
            "",
            "---",
            "",
            "## 关键发现",
            "",
            "- Project Copilot 已能在真实项目中形成可审阅的 `.ai/` 项目记忆。",
            "- ADR、Session Archive、候选事件、Charter 和 Roadmap 可以作为记忆质量验证的基础指标。",
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
            "- 纳入更多真实项目的 `.ai/validation.json`。",
            "- 从真实 `.ai` 自动刷新统计汇总。",
            "- 对比不同项目中的 ADR、Session Archive、候选事件和长期知识质量。",
            "- 继续减少人工维护的验证文档，避免验证体系漂移。",
            "",
        ]
    )
    return "\n".join(lines)


def _snapshot_to_record(snapshot: ValidationSnapshot, path: Path) -> ValidationRecord:
    return ValidationRecord(
        project_name=snapshot.project_name,
        started_at=snapshot.started_at or "待记录",
        status=snapshot.status or "待记录",
        usage_days=snapshot.usage_days,
        worklog_count=snapshot.worklog_count,
        decision_count=snapshot.decision_count,
        knowledge_count=snapshot.knowledge_count,
        adr_count=snapshot.adr_count,
        session_archive_count=snapshot.session_archive_count,
        active_candidate_count=snapshot.active_candidate_count,
        charter_present=snapshot.charter_present,
        roadmap_present=snapshot.roadmap_present,
        memory_health_status=snapshot.memory_health_status,
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


def _fmt_int(value: int | None) -> str:
    return str(value) if value is not None else "待记录"


def _fmt_bool(value: bool | None) -> str:
    if value is None:
        return "待记录"
    return "存在" if value else "缺失"


def _safe_exists(path: Path) -> bool:
    try:
        return path.exists()
    except OSError:
        return False
