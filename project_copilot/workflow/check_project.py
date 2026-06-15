from __future__ import annotations

from project_copilot.analyzer import analyze_project
from project_copilot.workflow.types import WorkflowContext
from project_copilot.workflow.utils import format_next_steps


def run(context: WorkflowContext) -> str:
    analysis = analyze_project(context.root)
    lines = [
        f"项目健康度评分：{analysis.health_score}/100",
        f"当前开发阶段：{analysis.stage}",
        f"Git：{'已初始化' if analysis.git.initialized else '未初始化'}",
    ]
    if analysis.git.branch:
        lines.append(f"当前分支：{analysis.git.branch}")
    if analysis.git.dirty_files:
        lines.append("未提交变更：" + ", ".join(analysis.git.dirty_files[:8]))
    if analysis.missing:
        lines.append("缺失文件：" + ", ".join(analysis.missing))
    if analysis.risks:
        lines.append("当前风险：" + "；".join(analysis.risks))
    lines.append(format_next_steps(analysis.next_steps))
    return "\n".join(lines)
