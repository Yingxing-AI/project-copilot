from __future__ import annotations

from project_copilot.oss import check_oss_readiness
from project_copilot.workflow.types import WorkflowContext


def run(context: WorkflowContext) -> str:
    readiness = check_oss_readiness(context.root)
    lines = [f"OSS Readiness Score：{readiness.score}/100"]
    if readiness.present:
        lines.append("已具备：" + ", ".join(readiness.present))
    if readiness.missing:
        lines.append("缺失：" + ", ".join(readiness.missing))
        lines.append("改进建议：" + "；".join(readiness.suggestions))
    return "\n".join(lines)
