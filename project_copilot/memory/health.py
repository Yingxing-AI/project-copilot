from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MemoryHealth:
    status: str
    charter_present: bool
    adr_count: int
    status_present: bool
    roadmap_present: bool
    session_archive_count: int
    active_candidate_count: int
    drift_signals: list[str]
    missing: list[str]
    roadmap_items: list[str]
    next_steps: list[str]


def inspect_memory_health(root: Path) -> MemoryHealth:
    ai_dir = root / ".ai"
    charter_present = _has_meaningful_file(ai_dir / "PROJECT_CHARTER.md")
    adr_count = _count_adr(ai_dir / "adr")
    status_present = _has_meaningful_file(ai_dir / "STATUS.md")
    roadmap_present = _has_meaningful_file(ai_dir / "ROADMAP.md")
    session_archive_count = _count_session_archives(ai_dir / "sessions" / "archive")
    active_candidate_count = _count_session_candidates(ai_dir / "sessions" / "current.md")
    roadmap_items = _roadmap_items(ai_dir / "ROADMAP.md")

    missing: list[str] = []
    if not charter_present:
        missing.append(".ai/PROJECT_CHARTER.md")
    if adr_count == 0:
        missing.append(".ai/adr/")
    if not status_present:
        missing.append(".ai/STATUS.md")
    if not roadmap_present:
        missing.append(".ai/ROADMAP.md")
    if not (ai_dir / "sessions" / "archive").exists():
        missing.append(".ai/sessions/archive/")

    drift_signals = _drift_signals(ai_dir, active_candidate_count)
    status = _status_label(missing, drift_signals)
    next_steps = _next_steps(missing, drift_signals, active_candidate_count)

    return MemoryHealth(
        status=status,
        charter_present=charter_present,
        adr_count=adr_count,
        status_present=status_present,
        roadmap_present=roadmap_present,
        session_archive_count=session_archive_count,
        active_candidate_count=active_candidate_count,
        drift_signals=drift_signals,
        missing=missing,
        roadmap_items=roadmap_items,
        next_steps=next_steps,
    )


def _has_meaningful_file(path: Path) -> bool:
    try:
        if not path.exists():
            return False
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return False
    return bool(text) and text not in {"暂无。", "暂无"}


def _count_adr(adr_dir: Path) -> int:
    try:
        if not adr_dir.exists():
            return 0
        return sum(1 for path in adr_dir.glob("*.md") if re.match(r"^\d{4}-", path.name))
    except OSError:
        return 0


def _count_session_archives(archive_dir: Path) -> int:
    try:
        if not archive_dir.exists():
            return 0
        count = 0
        for path in archive_dir.rglob("*.md"):
            if path.name.startswith("."):
                continue
            count += 1
        return count
    except OSError:
        return 0


def _count_session_candidates(path: Path) -> int:
    try:
        if not path.exists():
            return 0
        text = path.read_text(encoding="utf-8")
    except OSError:
        return 0
    count = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        if "暂无" in stripped or "说明：" in stripped:
            continue
        count += 1
    return count


def _roadmap_items(path: Path, limit: int = 5) -> list[str]:
    try:
        if not path.exists():
            return []
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- [ ]") or stripped.startswith("- [x]") or stripped.startswith("- [X]"):
            items.append(stripped)
    return items[:limit]


def _drift_signals(ai_dir: Path, active_candidate_count: int) -> list[str]:
    signals: list[str] = []
    if active_candidate_count:
        signals.append("存在未确认 Session 候选，尚未沉淀或丢弃。")
    if _has_non_placeholder_content(ai_dir / "HYPOTHESES.md"):
        signals.append("HYPOTHESES.md 仍有内容，应迁移为 Session 候选或明确标记 legacy。")
    if _has_active_worklog(ai_dir / "WORKLOG.md"):
        signals.append("WORKLOG.md 仍有活跃流水账，应降级为 legacy 或迁移到 session archive 派生。")
    if (ai_dir / "metrics.md").exists():
        signals.append("metrics.md 是手工快照风险点，后续应迁移为 derived/metrics.json。")
    return signals


def _has_non_placeholder_content(path: Path) -> bool:
    try:
        if not path.exists():
            return False
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        if "暂无" in stripped:
            continue
        return True
    return False


def _has_active_worklog(path: Path) -> bool:
    try:
        if not path.exists():
            return False
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return bool(re.search(r"^##\s+\d{4}-\d{2}-\d{2}|^- 完成内容：", text, flags=re.MULTILINE))


def _status_label(missing: list[str], drift_signals: list[str]) -> str:
    if missing:
        return "需要补齐记忆层"
    if drift_signals:
        return "需要收敛记忆漂移"
    return "记忆层可用"


def _next_steps(missing: list[str], drift_signals: list[str], active_candidate_count: int) -> list[str]:
    steps: list[str] = []
    if missing:
        steps.append("先补齐缺失的核心记忆文件或执行 adopt_project。")
    if active_candidate_count:
        steps.append("结束工作时确认 Session 候选，决定写入 ADR、history、knowledge 或丢弃。")
    if drift_signals:
        steps.append("优先把长期事实、假设、计划、决策重新分层，避免写入 MEMORY/WORKLOG 噪音。")
    if not steps:
        steps.append("开始工作读取 Charter、Status、Roadmap 和 ADR；结束工作统一沉淀 Session。")
    return steps
