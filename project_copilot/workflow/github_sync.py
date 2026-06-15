from __future__ import annotations

from project_copilot.gitops import build_github_sync_plan, sync_to_github
from project_copilot.workflow.types import WorkflowContext


EXECUTE_KEYWORDS = ("执行同步", "立即同步", "直接同步", "push")


def run(context: WorkflowContext) -> str:
    execute = any(keyword in context.text.lower() for keyword in EXECUTE_KEYWORDS)
    plan = sync_to_github(context.root, context.text) if execute else build_github_sync_plan(context.root, context.text)

    lines = [
        "GitHub 同步计划",
        f"仓库可见性：{plan.visibility}",
        f"仓库名称：{plan.repo_name}",
        f"GitHub CLI：{'可用' if plan.gh_available else '不可用'}",
        f"GitHub 登录：{'已登录' if plan.gh_authenticated else '未登录'}",
    ]
    if plan.existing_remote:
        lines.append(f"现有 remote：{plan.existing_remote}")
    if plan.repo_url:
        lines.append(f"目标仓库：{plan.repo_url}")
    lines.append("计划动作：")
    lines.extend(f"- {action}" for action in plan.actions)
    if plan.blockers:
        lines.append("阻塞项：")
        lines.extend(f"- {blocker}" for blocker in plan.blockers)
    elif execute:
        lines.append("同步状态：已执行。")
    else:
        lines.append("同步状态：待执行。确认后可说“执行同步到 GitHub”。")
    return "\n".join(lines)
