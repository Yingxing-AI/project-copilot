from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from project_copilot.analyzer import analyze_project


@dataclass(frozen=True)
class ValidationSnapshot:
    project_name: str
    started_at: str
    status: str
    usage_days: int | None = None
    worklog_count: int | None = None
    decision_count: int | None = None
    knowledge_count: int | None = None
    project_health: int | None = None
    roadmap_state: str | None = None
    source: str = "project-copilot validation snapshot"
    updated_at: str | None = None


def load_validation_snapshot(path: Path) -> ValidationSnapshot | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return ValidationSnapshot(
        project_name=str(data.get("project_name", "")).strip(),
        started_at=str(data.get("started_at", "")).strip(),
        status=str(data.get("status", "")).strip(),
        usage_days=_maybe_int(data.get("usage_days")),
        worklog_count=_maybe_int(data.get("worklog_count")),
        decision_count=_maybe_int(data.get("decision_count")),
        knowledge_count=_maybe_int(data.get("knowledge_count")),
        project_health=_maybe_int(data.get("project_health")),
        roadmap_state=str(data.get("roadmap_state", "")).strip() or None,
        source=str(data.get("source", "project-copilot validation snapshot")).strip(),
        updated_at=str(data.get("updated_at", "")).strip() or None,
    )


def collect_validation_snapshot(root: Path) -> ValidationSnapshot | None:
    try:
        ai_dir = root / ".ai"
        if not _safe_exists(ai_dir):
            return None

        project_name = (
            _extract_meaningful_field(ai_dir / "PROJECT_CHARTER.md", "项目名称")
            or _extract_meaningful_field(ai_dir / "PROJECT_CONTEXT.md", "项目名称")
            or root.name
        )
        started_at = _started_at_from_ai(ai_dir)
        status = _extract_field(ai_dir / "STATUS.md", "当前阶段") or "待记录"
        usage_days = _usage_days(started_at)
        worklog_count = _count_worklog_entries(ai_dir / "WORKLOG.md")
        decision_count = _count_decisions(ai_dir)
        knowledge_count = _count_knowledge_entries(ai_dir / "KNOWLEDGE.md")
        roadmap_state = _roadmap_state(ai_dir / "ROADMAP.md")
        project_health = analyze_project(root).health_score
    except OSError:
        return None

    return ValidationSnapshot(
        project_name=project_name,
        started_at=started_at or "",
        status=status,
        usage_days=usage_days,
        worklog_count=worklog_count,
        decision_count=decision_count,
        knowledge_count=knowledge_count,
        project_health=project_health,
        roadmap_state=roadmap_state,
        source="auto_collected_from_ai",
    )


def export_validation_snapshot(root: Path, snapshot: ValidationSnapshot) -> Path:
    ai_dir = root / ".ai"
    ai_dir.mkdir(parents=True, exist_ok=True)
    payload = asdict(snapshot)
    payload["updated_at"] = snapshot.updated_at or datetime.now().isoformat(timespec="seconds")
    path = ai_dir / "validation.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _maybe_int(value: object) -> int | None:
    if value in (None, "", []):
        return None
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _extract_field(path: Path, field_name: str) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    pattern = rf"^{re.escape(field_name)}：(.+)$"
    match = re.search(pattern, text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _extract_meaningful_field(path: Path, field_name: str) -> str:
    value = _extract_field(path, field_name)
    return "" if value in {"待确认", "待确认。", "待补充", "待补充。"} else value


def _started_at_from_ai(ai_dir: Path) -> str:
    candidates = [
        ai_dir / "PROJECT_CONTEXT.md",
        ai_dir / "PROJECT_CHARTER.md",
        ai_dir / "STATUS.md",
        ai_dir / "MEMORY.md",
        ai_dir / "HYPOTHESES.md",
        ai_dir / "ROADMAP.md",
        ai_dir / "DECISIONS.md",
        ai_dir / "WORKLOG.md",
        ai_dir / "KNOWLEDGE.md",
    ]
    mtimes = []
    for path in candidates:
        if not _safe_exists(path):
            continue
        try:
            mtimes.append(path.stat().st_mtime)
        except OSError:
            continue
    if not mtimes:
        return ""
    return datetime.fromtimestamp(min(mtimes)).date().isoformat()


def _usage_days(started_at: str) -> int | None:
    if not started_at:
        return None
    try:
        start = datetime.fromisoformat(started_at).date()
    except ValueError:
        return None
    return max(0, (datetime.now().date() - start).days)


def _count_worklog_entries(path: Path) -> int | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    heading_count = len(re.findall(r"^##\s+\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?\s*$", text, flags=re.MULTILINE))
    if heading_count:
        return heading_count
    legacy_count = len(re.findall(r"^\d{4}-\d{2}-\d{2}\s*$", text, flags=re.MULTILINE))
    if legacy_count:
        return legacy_count
    fallback_count = len(re.findall(r"^- 完成内容：", text, flags=re.MULTILINE))
    return fallback_count


def _count_decisions(ai_dir: Path) -> int | None:
    adr_count = _count_adr_entries(ai_dir / "adr")
    if adr_count:
        return adr_count
    path = ai_dir / "DECISIONS.md"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    heading_count = len(re.findall(r"^##\s+\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?\s*$", text, flags=re.MULTILINE))
    if heading_count:
        return heading_count
    legacy_count = len(re.findall(r"^日期：", text, flags=re.MULTILINE))
    if legacy_count:
        return legacy_count
    fallback_count = len(re.findall(r"^- 决策：", text, flags=re.MULTILINE))
    return fallback_count


def _count_adr_entries(adr_dir: Path) -> int:
    if not adr_dir.exists():
        return 0
    count = 0
    for path in adr_dir.glob("*.md"):
        if path.name == "index.md":
            continue
        if re.match(r"^\d{4}-", path.name):
            count += 1
    return count


def _count_knowledge_entries(path: Path) -> int | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    count = 0
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and "暂无" not in stripped:
            count += 1
    return count


def _roadmap_state(path: Path) -> str | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    in_progress = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_progress = stripped == "## In Progress"
            continue
        if in_progress and stripped.startswith("- [ ]"):
            return stripped.removeprefix("- [ ]").strip() or "进行中"
    return None


def _safe_exists(path: Path) -> bool:
    try:
        return path.exists()
    except OSError:
        return False
