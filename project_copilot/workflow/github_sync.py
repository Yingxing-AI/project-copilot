from __future__ import annotations

from project_copilot.gitops import build_github_sync_plan, sync_to_github
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


EXECUTE_KEYWORDS = ("执行同步", "立即同步", "直接同步", "执行备份", "push")


def run(context: WorkflowContext) -> WorkflowResult:
    execute = any(keyword in context.text.lower() for keyword in EXECUTE_KEYWORDS)
    plan = sync_to_github(context.root, context.text) if execute else build_github_sync_plan(context.root, context.text)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="blocked" if plan.blockers else "success",
        title="云端备份计划",
        summary="备份状态：已执行。" if execute and not plan.blockers else "备份状态：待执行。",
        details={
            "备份空间": _visibility_label(plan.visibility),
            "项目名称": plan.repo_name,
            "云端工具": "可用" if plan.gh_available else "不可用",
            "云端登录": "已登录" if plan.gh_authenticated else "未登录",
            "现有云端地址": plan.existing_remote,
            "目标云端地址": plan.repo_url,
            "计划动作": [_soften_action(action) for action in plan.actions],
            "阻塞项": [_soften_blocker(blocker) for blocker in plan.blockers],
        },
        next_steps=[] if plan.blockers else ["确认后可说“执行备份到云端”。"],
    )


def _visibility_label(visibility: str) -> str:
    return "私有备份" if visibility == "private" else "公开备份"


def _soften_action(action: str) -> str:
    replacements = {
        "初始化当前目录为独立 Git 仓库（如尚未初始化）。": "建立本地保存进度记录（如尚未建立）。",
        "生成提交并推送到 GitHub。": "保存当前进度并备份到云端。",
    }
    if action in replacements:
        return replacements[action]
    if action.startswith("使用现有 remote origin："):
        return "使用现有云端备份地址。"
    if action.startswith("通过 GitHub CLI 创建"):
        return "创建云端备份空间。"
    if action == "等待用户提供 GitHub 仓库地址，或安装 GitHub CLI。":
        return "等待用户提供云端备份地址，或安装云端备份工具。"
    return action.replace("GitHub", "云端").replace("Git", "保存进度记录").replace("push", "备份")


def _soften_blocker(blocker: str) -> str:
    return (
        blocker.replace("GitHub CLI", "云端备份工具")
        .replace("gh auth login", "云端工具登录")
        .replace("remote origin", "云端备份地址")
        .replace("Git 仓库", "保存进度记录")
    )
