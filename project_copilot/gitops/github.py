from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from project_copilot.gitops.repo import init_git_if_needed


REMOTE_RE = re.compile(r"(git@github\.com:[\w.-]+/[\w.-]+\.git|https://github\.com/[\w.-]+/[\w.-]+(?:\.git)?)")


@dataclass(frozen=True)
class GitHubSyncPlan:
    visibility: str
    repo_name: str
    repo_url: str | None
    existing_remote: str | None
    gh_available: bool
    gh_authenticated: bool
    can_sync: bool
    actions: list[str]
    blockers: list[str]


def build_github_sync_plan(root: Path, text: str) -> GitHubSyncPlan:
    root.mkdir(parents=True, exist_ok=True)
    visibility = _detect_visibility(text)
    repo_name = _extract_repo_name(text) or root.name
    repo_url = _extract_repo_url(text)
    existing_remote = _get_origin_remote(root)
    parent_git_root = _get_parent_git_root(root)
    gh_available = shutil.which("gh") is not None
    gh_authenticated = _is_gh_authenticated(root) if gh_available else False

    actions = [
        "初始化当前目录为独立 Git 仓库（如尚未初始化）。",
        "生成提交并推送到 GitHub。",
    ]
    if existing_remote:
        actions.insert(1, f"使用现有 remote origin：{existing_remote}")
    elif repo_url:
        actions.insert(1, f"添加 remote origin：{repo_url}")
    elif gh_available:
        actions.insert(1, f"通过 GitHub CLI 创建 {visibility} 仓库：{repo_name}")
    else:
        actions.insert(1, "等待用户提供 GitHub 仓库地址，或安装 GitHub CLI。")

    blockers: list[str] = []
    if parent_git_root and not existing_remote:
        actions.insert(1, f"忽略上级 Git 仓库 {parent_git_root} 的 remote。")
    if not existing_remote and not repo_url:
        if not gh_available:
            blockers.append("缺少 GitHub 仓库地址，且当前环境没有 gh CLI，无法自动创建远程仓库。")
        elif not gh_authenticated:
            blockers.append("GitHub CLI 尚未登录，请先运行 gh auth login。")

    return GitHubSyncPlan(
        visibility=visibility,
        repo_name=repo_name,
        repo_url=repo_url,
        existing_remote=existing_remote,
        gh_available=gh_available,
        gh_authenticated=gh_authenticated,
        can_sync=not blockers,
        actions=actions,
        blockers=blockers,
    )


def sync_to_github(root: Path, text: str, commit_message: str = "chore: prepare project copilot") -> GitHubSyncPlan:
    plan = build_github_sync_plan(root, text)
    if not plan.can_sync:
        return plan

    init_git_if_needed(root)
    if plan.repo_url and not plan.existing_remote:
        _run(root, ["git", "remote", "add", "origin", plan.repo_url])
    elif not plan.existing_remote:
        create = _run(
            root,
            [
                "gh",
                "repo",
                "create",
                plan.repo_name,
                f"--{plan.visibility}",
                "--source",
                str(root),
                "--remote",
                "origin",
            ],
        )
        if create.returncode != 0:
            return _blocked_plan(plan, create.stderr.strip() or create.stdout.strip())

    _run(root, ["git", "add", "."])
    commit = _run(root, ["git", "commit", "-m", commit_message])
    if commit.returncode != 0 and "nothing to commit" not in (commit.stdout + commit.stderr).lower():
        return _blocked_plan(plan, commit.stderr.strip() or commit.stdout.strip())
    _run(root, ["git", "branch", "-M", "main"])
    push = _run(root, ["git", "push", "-u", "origin", "main"])
    if push.returncode != 0:
        return _blocked_plan(plan, push.stderr.strip() or push.stdout.strip())
    return plan


def _detect_visibility(text: str) -> str:
    normalized = text.lower()
    if "私有" in normalized or "private" in normalized:
        return "private"
    if "开源" in normalized or "公开" in normalized or "public" in normalized:
        return "public"
    return "public"


def _extract_repo_url(text: str) -> str | None:
    match = REMOTE_RE.search(text)
    return match.group(1) if match else None


def _extract_repo_name(text: str) -> str | None:
    match = re.search(r"(?:仓库名|repo|repository)[:：= ]+([\w.-]+(?:/[\w.-]+)?)", text, flags=re.IGNORECASE)
    return match.group(1) if match else None


def _get_origin_remote(root: Path) -> str | None:
    if _get_exact_git_root(root) != root.resolve():
        return None
    result = _run(root, ["git", "remote", "get-url", "origin"])
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _get_exact_git_root(root: Path) -> Path | None:
    result = _run(root, ["git", "rev-parse", "--show-toplevel"])
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip()).resolve()


def _get_parent_git_root(root: Path) -> Path | None:
    git_root = _get_exact_git_root(root)
    if git_root and git_root != root.resolve():
        return git_root
    return None


def _is_gh_authenticated(root: Path) -> bool:
    config_home = Path.home() / ".config" / "gh" / "hosts.yml"
    if config_home.exists() and "github.com" in config_home.read_text(encoding="utf-8"):
        return True
    return _run(root, ["gh", "auth", "status"]).returncode == 0


def _blocked_plan(plan: GitHubSyncPlan, blocker: str) -> GitHubSyncPlan:
    return GitHubSyncPlan(
        plan.visibility,
        plan.repo_name,
        plan.repo_url,
        plan.existing_remote,
        plan.gh_available,
        plan.gh_authenticated,
        False,
        plan.actions,
        [blocker],
    )


def _run(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
