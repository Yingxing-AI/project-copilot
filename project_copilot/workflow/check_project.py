from __future__ import annotations

from project_copilot.secretary import inspect_secretary_status
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    secretary_status = inspect_secretary_status(context.root)
    analysis = secretary_status.analysis
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="项目状态卡片",
        summary=f"项目健康度：{analysis.health_score}/100",
        details={
            "当前阶段": analysis.stage,
            "距离上次复盘": _format_days(secretary_status.days_since_review),
            "路线图更新": _format_days(secretary_status.days_since_roadmap_update),
            "待补齐项目档案": analysis.missing,
            "当前风险": analysis.risks,
            "提醒": secretary_status.reminders,
        },
        next_steps=analysis.next_steps,
    )


def _format_days(days: int | None) -> str:
    if days is None:
        return "暂无记录"
    if days == 0:
        return "今天"
    return f"{days}天"
