from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from project_copilot.analyzer import ProjectAnalysis, analyze_project


@dataclass(frozen=True)
class SecretaryStatus:
    analysis: ProjectAnalysis
    days_since_work: int | None
    days_since_review: int | None
    days_since_roadmap_update: int | None
    reminders: list[str]


def inspect_secretary_status(root: Path) -> SecretaryStatus:
    analysis = analyze_project(root)
    days_since_work = _days_since_worklog(root / ".ai" / "WORKLOG.md")
    days_since_review = _days_since_latest_review(root / ".ai" / "history")
    days_since_roadmap_update = _days_since_file(root / ".ai" / "ROADMAP.md")
    reminders = _build_reminders(analysis, days_since_review, days_since_roadmap_update)
    return SecretaryStatus(
        analysis=analysis,
        days_since_work=days_since_work,
        days_since_review=days_since_review,
        days_since_roadmap_update=days_since_roadmap_update,
        reminders=reminders,
    )


def render_secretary_intro() -> str:
    return "\n".join(
        [
            "你好，我是你的项目秘书。",
            "",
            "我会帮你：",
            "",
            "* 记录项目历史",
            "* 保存重要决策",
            "* 提醒项目风险",
            "* 防止项目跑偏",
            "",
            "Codex 负责开发，",
            "我负责记住。",
        ]
    )


def render_status_card(root: Path) -> str:
    status = inspect_secretary_status(root)
    analysis = status.analysis
    project_name = _project_name(root)
    lines = [
        f"📌 项目：{project_name}",
        "",
        "项目状态：",
        f"{status_label_from_health_score(analysis.health_score)}（{analysis.health_score}）",
        "",
        "当前阶段：",
        _friendly_stage(analysis.stage),
        "",
        "最近一次工作：",
        _format_days(status.days_since_work),
        "",
        "最近一次复盘：",
        _format_days(status.days_since_review),
        "",
        "提醒：",
    ]
    if status.reminders:
        lines.extend(f"⚠ {item}" for item in status.reminders)
    else:
        lines.append("暂无需要立即处理的提醒。")
    return "\n".join(lines)


def render_recommended_commands() -> str:
    return "\n".join(
        [
            "建议你现在可以输入：",
            "",
            "项目复盘",
            "结束工作",
            "项目时间轴",
            "项目偏航检查",
            "记录决策",
            "查看路线图",
            "",
            "输入 退出 结束。",
        ]
    )


def render_noninteractive_help() -> str:
    return "\n".join(
        [
            "当前环境无法保持连续交互输入。",
            "",
            "如果你想让我继续，可以让我执行：",
            "",
            "project-copilot 项目复盘",
            "",
            "project-copilot 结束工作",
            "",
            "project-copilot 项目时间轴",
            "",
            "project-copilot 项目偏航检查",
        ]
    )


def status_label_from_health_score(score: int) -> str:
    if score >= 85:
        return "🟢 进展良好"
    if score >= 60:
        return "🟡 需要关注"
    return "🔴 存在风险"


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


def _days_since_worklog(path: Path) -> int | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    if "暂无工作记录" in text and "- " not in text:
        return None
    return _days_since_file(path)


def _days_since_latest_review(history_dir: Path) -> int | None:
    candidates = []
    if history_dir.exists():
        candidates.extend(path for path in history_dir.iterdir() if path.is_file() and not path.name.startswith("."))
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


def _friendly_stage(stage: str) -> str:
    normalized = stage.replace(" ", "")
    if normalized in {"可持续开发", "验证阶段"}:
        return stage
    if "MVP" in stage or "初始化" in stage or "未初始化" in stage:
        return "MVP开发"
    return stage
