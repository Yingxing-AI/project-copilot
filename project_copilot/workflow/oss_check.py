from __future__ import annotations

from project_copilot.oss import check_oss_readiness
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    readiness = check_oss_readiness(context.root)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="OSS 准备度检查完成。",
        summary=f"OSS Readiness Score：{readiness.score}/100",
        details={"已具备": readiness.present, "缺失": readiness.missing},
        next_steps=readiness.suggestions,
    )
