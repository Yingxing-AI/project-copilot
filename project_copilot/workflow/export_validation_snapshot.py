from __future__ import annotations

from project_copilot.validation import export_validation_snapshot
from project_copilot.validation.snapshot import collect_validation_snapshot
from project_copilot.validation.report import refresh_validation_report
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
    report_path, records = refresh_validation_report(context.root)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已导出验证快照。",
        summary="已从 `.ai` 记忆写入验证快照，并刷新验证报告。",
        details={
            "项目名称": snapshot.project_name,
            "开始日期": snapshot.started_at,
            "状态": snapshot.status,
            "工作日志": snapshot.worklog_count,
            "决策": snapshot.decision_count,
            "知识沉淀": snapshot.knowledge_count,
            "更新文件": [str(path.relative_to(context.root)), str(report_path.relative_to(context.root))],
            "项目数量": len(records),
        },
        next_steps=["长期记忆或验证快照写入后会自动刷新；手动刷新只作为修复或兼容命令保留。"],
    )
