from __future__ import annotations

from project_copilot.validation import export_validation_snapshot
from project_copilot.validation.snapshot import collect_validation_snapshot
from project_copilot.memory import MemoryStore
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    memory = MemoryStore(context.root)
    memory.ensure()
    snapshot = collect_validation_snapshot(context.root)
    if not snapshot:
        return WorkflowResult(
            intent_name=context.intent_name,
            status="needs_input",
            title="需要项目记忆才能导出验证快照。",
            summary="请先完成 .ai/ 记忆初始化，再导出 validation.json。",
            next_steps=["先运行初始化或接管项目，再重新导出验证快照。"],
        )

    path = export_validation_snapshot(context.root, snapshot)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已导出验证快照。",
        summary=f"已从 `.ai` 记忆写入 {path.relative_to(context.root)}",
        details={
            "项目名称": snapshot.project_name,
            "开始日期": snapshot.started_at,
            "状态": snapshot.status,
            "工作日志": snapshot.worklog_count,
            "决策": snapshot.decision_count,
            "知识沉淀": snapshot.knowledge_count,
        },
        next_steps=["系统会在关键工作流后自动刷新汇总；也可以手动运行“刷新验证报告”。"],
    )
