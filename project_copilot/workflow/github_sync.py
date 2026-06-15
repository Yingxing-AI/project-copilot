from __future__ import annotations

from project_copilot.gitops import build_github_sync_plan, sync_to_github
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


EXECUTE_KEYWORDS = ("执行同步", "立即同步", "直接同步", "push")


def run(context: WorkflowContext) -> WorkflowResult:
    execute = any(keyword in context.text.lower() for keyword in EXECUTE_KEYWORDS)
    plan = sync_to_github(context.root, context.text) if execute else build_github_sync_plan(context.root, context.text)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="blocked" if plan.blockers else "success",
        title="GitHub 同步计划",
        summary="同步状态：已执行。" if execute and not plan.blockers else "同步状态：待执行。",
        details={
            "仓库可见性": plan.visibility,
            "仓库名称": plan.repo_name,
            "GitHub CLI": "可用" if plan.gh_available else "不可用",
            "GitHub 登录": "已登录" if plan.gh_authenticated else "未登录",
            "现有 remote": plan.existing_remote,
            "目标仓库": plan.repo_url,
            "计划动作": plan.actions,
            "阻塞项": plan.blockers,
        },
        next_steps=[] if plan.blockers else ["确认后可说“执行同步到 GitHub”。"],
    )
