from __future__ import annotations

from project_copilot.analyzer import analyze_project
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    analysis = analyze_project(context.root)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="项目状态检查完成。",
        summary=f"项目健康度评分：{analysis.health_score}/100",
        details={
            "当前开发阶段": analysis.stage,
            "Git": "已初始化" if analysis.git.initialized else "未初始化",
            "当前分支": analysis.git.branch,
            "未提交变更": analysis.git.dirty_files[:8],
            "缺失文件": analysis.missing,
            "当前风险": analysis.risks,
        },
        next_steps=analysis.next_steps,
    )
