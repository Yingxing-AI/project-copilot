from __future__ import annotations

from project_copilot.validation import refresh_validation_report
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    report_path, records = refresh_validation_report(context.root)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已刷新验证报告。",
        summary="已从 `.ai` 记忆和验证快照重建统计汇总。",
        details={
            "更新文件": [str(report_path.relative_to(context.root))],
            "项目数量": len(records),
            "数据源": [record.project_name for record in records],
        },
        next_steps=["如果有新的项目记忆变更，系统会自动刷新；也可以手动重新运行“刷新验证报告”。"],
    )
