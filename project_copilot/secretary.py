from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from project_copilot.analyzer import ProjectAnalysis, analyze_project


@dataclass(frozen=True)
class SecretaryStatus:
    analysis: ProjectAnalysis
    days_since_review: int | None
    days_since_roadmap_update: int | None
    reminders: list[str]


def inspect_secretary_status(root: Path) -> SecretaryStatus:
    analysis = analyze_project(root)
    days_since_review = _days_since_latest(root / ".ai" / "history", root / ".ai" / "WORKLOG.md")
    days_since_roadmap_update = _days_since_file(root / ".ai" / "ROADMAP.md")
    reminders = _build_reminders(analysis, days_since_review, days_since_roadmap_update)
    return SecretaryStatus(
        analysis=analysis,
        days_since_review=days_since_review,
        days_since_roadmap_update=days_since_roadmap_update,
        reminders=reminders,
    )


def render_status_card(root: Path) -> str:
    status = inspect_secretary_status(root)
    analysis = status.analysis
    project_name = _project_name(root)
    lines = [
        "项目状态卡片",
        "",
        f"项目：{project_name}",
        f"当前阶段：{analysis.stage}",
        f"项目健康度：{analysis.health_score}",
        f"距离上次复盘：{_format_days(status.days_since_review)}",
        f"路线图更新：{_format_days(status.days_since_roadmap_update)}",
        "",
        "提醒：",
    ]
    if status.reminders:
        lines.extend(f"- {item}" for item in status.reminders)
    else:
        lines.append("- 暂无需要立即处理的提醒。")
    return "\n".join(lines)


def _build_reminders(
    analysis: ProjectAnalysis,
    days_since_review: int | None,
    days_since_roadmap_update: int | None,
) -> list[str]:
    reminders: list[str] = []
    if days_since_review is None:
        reminders.append("还没有项目复盘记录，建议完成一次项目复盘。")
    elif days_since_review >= 7:
        reminders.append("距离上次复盘超过 7 天，建议进行一次项目复盘。")

    if days_since_roadmap_update is None:
        reminders.append("还没有路线图记录，建议先明确 MVP。")
    elif days_since_roadmap_update >= 14:
        reminders.append("已连续 14 天未更新路线图。")

    reminders.extend(analysis.risks[:3])
    return reminders


def _project_name(root: Path) -> str:
    context = root / ".ai" / "PROJECT_CONTEXT.md"
    if context.exists():
        for line in context.read_text(encoding="utf-8").splitlines():
            if line.startswith("项目名称："):
                name = line.split("：", 1)[1].strip()
                if name:
                    return name
    return root.name


def _days_since_latest(history_dir: Path, fallback: Path) -> int | None:
    candidates = []
    if history_dir.exists():
        candidates.extend(path for path in history_dir.iterdir() if path.is_file())
    if fallback.exists():
        candidates.append(fallback)
    if not candidates:
        return None
    latest = max(path.stat().st_mtime for path in candidates)
    return max(0, (datetime.now() - datetime.fromtimestamp(latest)).days)


def _days_since_file(path: Path) -> int | None:
    if not path.exists():
        return None
    return max(0, (datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)).days)


def _format_days(days: int | None) -> str:
    if days is None:
        return "暂无记录"
    if days == 0:
        return "今天"
    return f"{days}天"
