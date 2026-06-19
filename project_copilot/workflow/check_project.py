from __future__ import annotations

from project_copilot.memory.health import inspect_memory_health
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    health = inspect_memory_health(context.root)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="Memory Health Summary",
        summary=f"记忆层状态：{health.status}",
        details={
            "Project Charter": "存在" if health.charter_present else "缺失",
            "ADR 数": health.adr_count,
            "当前 STATUS": "存在" if health.status_present else "缺失",
            "Roadmap": "存在" if health.roadmap_present else "缺失",
            "Session Archive 数": health.session_archive_count,
            "Active Candidates 数": health.active_candidate_count,
            "Roadmap 派生视图": health.roadmap_items,
            "缺失项": health.missing,
            "记忆漂移": health.drift_signals or ["未发现明显记忆漂移。"],
        },
        next_steps=health.next_steps,
    )
