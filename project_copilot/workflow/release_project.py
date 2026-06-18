from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from project_copilot.workflow.sync_project_state import sync_project_state
from project_copilot.workflow.types import WorkflowContext, WorkflowResult
from project_copilot import __version__

Runner = Callable[[Path, list[str]], subprocess.CompletedProcess[str]]

TAG_RE = re.compile(r"\bv?\d+\.\d+\.\d+(?:[-.][0-9A-Za-z.-]+)?\b")


@dataclass
class ReleaseOutcome:
    tag: str
    status: str
    actions: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    release_notes: Path | None = None
    dry_run: bool = False


def run(context: WorkflowContext) -> WorkflowResult:
    tag = extract_tag(context.text)
    if not tag:
        return WorkflowResult(
            intent_name=context.intent_name,
            status="blocked",
            title="发布被阻止。",
            summary="请提供明确版本标记，例如：project-copilot 发布版本 v0.3.0-beta.2",
            next_steps=["输入 `project-copilot 发布版本 v0.3.0-beta.2`。"],
        )

    dry_run = _is_dry_run(context.text)
    outcome = release_project(context.root, tag, dry_run=dry_run)
    return WorkflowResult(
        intent_name=context.intent_name,
        status=outcome.status,
        title=_release_title(outcome),
        summary=f"目标版本标记：{outcome.tag}",
        details={
            "计划动作" if outcome.dry_run else "已执行": [_soften_release_action(action) for action in outcome.actions],
            "阻塞项": [_soften_blocker(blocker) for blocker in outcome.blockers],
            "发布说明": str(outcome.release_notes) if outcome.release_notes else None,
        },
        next_steps=_release_next_steps(outcome),
    )


def release_project(root: Path, tag: str, runner: Runner | None = None, dry_run: bool = False) -> ReleaseOutcome:
    runner = runner or _run
    outcome = ReleaseOutcome(tag=tag, status="blocked", dry_run=dry_run)
    blockers = _preflight(root, tag, runner, require_gh_auth=not dry_run)
    if blockers:
        outcome.blockers.extend(blockers)
        return outcome

    planned_actions = [
        "同步项目状态",
        "pytest -q",
        "生成 release notes",
        "git add .",
        f"git commit -m chore: prepare release {tag}",
        "git push origin main",
        f"git tag -a {tag}",
        f"git push origin {tag}",
        "gh release create",
    ]
    if dry_run:
        outcome.status = "success"
        outcome.actions.extend(planned_actions)
        return outcome

    sync = sync_project_state(root)
    if sync.updated_files:
        outcome.actions.append("同步项目状态")

    test = runner(root, ["pytest", "-q"])
    if test.returncode != 0:
        outcome.blockers.append("测试失败：pytest -q")
        return outcome
    outcome.actions.append("pytest -q")

    notes = _write_release_notes(root, tag, runner)
    outcome.release_notes = notes
    outcome.actions.append("生成 release notes")

    if _has_changes(root, runner):
        for args, label in (
            (["git", "add", "."], "git add ."),
            (["git", "commit", "-m", f"chore: prepare release {tag}"], f"git commit -m chore: prepare release {tag}"),
        ):
            result = runner(root, args)
            if result.returncode != 0:
                outcome.blockers.append(_command_error(label, result))
                return outcome
            outcome.actions.append(label)

    for args, label in (
        (["git", "push", "origin", "main"], "git push origin main"),
        (["git", "tag", "-a", tag, "-m", f"Project Copilot {tag}"], f"git tag -a {tag}"),
        (["git", "push", "origin", tag], f"git push origin {tag}"),
    ):
        result = runner(root, args)
        if result.returncode != 0:
            outcome.blockers.append(_command_error(label, result))
            return outcome
        outcome.actions.append(label)

    release = runner(root, ["gh", "release", "create", tag, "--title", tag, "--notes-file", str(notes)])
    if release.returncode != 0:
        outcome.blockers.append(_command_error("gh release create", release))
        return outcome
    outcome.actions.append("gh release create")

    post_sync = sync_project_state(root)
    if post_sync.updated_files:
        outcome.actions.append("发布后同步项目状态")
        if _has_changes(root, runner):
            for args, label in (
                (["git", "add", "."], "git add ."),
                (["git", "commit", "-m", f"chore: sync release state {tag}"], f"git commit -m chore: sync release state {tag}"),
                (["git", "push", "origin", "main"], "git push origin main"),
            ):
                result = runner(root, args)
                if result.returncode != 0:
                    outcome.blockers.append(_command_error(label, result))
                    return outcome
                outcome.actions.append(label)
    outcome.status = "success"
    return outcome


def extract_tag(text: str) -> str | None:
    match = TAG_RE.search(text)
    return match.group(0) if match else None


def _is_dry_run(text: str) -> bool:
    normalized = text.lower()
    return any(token in normalized for token in ("dry-run", "dry run", "预演", "演练", "只检查", "preflight"))


def _preflight(root: Path, tag: str, runner: Runner, require_gh_auth: bool = True) -> list[str]:
    blockers: list[str] = []
    expected_version = _tag_to_pep440_version(tag)
    if expected_version and expected_version != __version__:
        blockers.append(f"版本不匹配：tag {tag} 对应 {expected_version}，当前包版本是 {__version__}。")
    if _git(root, ["rev-parse", "--is-inside-work-tree"], runner) != "true":
        blockers.append("当前目录不是 Git 仓库。")
    branch = _git(root, ["branch", "--show-current"], runner)
    if branch != "main":
        blockers.append(f"当前分支不是 main：{branch or 'unknown'}")
    if not _git(root, ["remote", "get-url", "origin"], runner):
        blockers.append("缺少 remote origin。")
    if _git(root, ["tag", "--list", tag], runner):
        blockers.append(f"标签已存在：{tag}")
    if runner(root, ["gh", "--version"]).returncode != 0:
        blockers.append("缺少 GitHub CLI：gh。")
    elif require_gh_auth and runner(root, ["gh", "auth", "status"]).returncode != 0:
        blockers.append("GitHub CLI 未登录，请先运行 gh auth login。")
    return blockers


def _tag_to_pep440_version(tag: str) -> str | None:
    normalized = tag[1:] if tag.startswith("v") else tag
    match = re.fullmatch(r"(\d+\.\d+\.\d+)-(alpha|beta)\.(\d+)", normalized)
    if match:
        suffix = "a" if match.group(2) == "alpha" else "b"
        return f"{match.group(1)}{suffix}{match.group(3)}"
    return normalized if re.fullmatch(r"\d+\.\d+\.\d+(?:a\d+)?", normalized) else None


def _release_title(outcome: ReleaseOutcome) -> str:
    if outcome.status != "success":
        return "发布被阻止。"
    return "发布预演完成。" if outcome.dry_run else "发布完成。"


def _release_next_steps(outcome: ReleaseOutcome) -> list[str]:
    if outcome.status != "success":
        return ["修复阻塞项后重新运行发布命令。"]
    if outcome.dry_run:
        return [f"确认无误后运行 `project-copilot 发布版本 {outcome.tag}`。"]
    return []


def _soften_release_action(action: str) -> str:
    replacements = {
        "同步项目状态": "同步项目状态",
        "pytest -q": "运行测试",
        "生成 release notes": "生成发布说明",
        "git add .": "整理待保存内容",
        "git push origin main": "备份到云端",
        "gh release create": "创建发布版本",
    }
    if action in replacements:
        return replacements[action]
    if action.startswith("git commit"):
        return "保存发布进度"
    if action.startswith("git tag"):
        return "创建版本标记"
    if action.startswith("git push origin"):
        return "备份版本标记到云端"
    return action


def _soften_blocker(blocker: str) -> str:
    return (
        blocker.replace("tag", "版本标记")
        .replace("Git 仓库", "保存进度记录")
        .replace("当前分支", "当前保存分支")
        .replace("remote origin", "云端备份地址")
        .replace("标签", "版本标记")
        .replace("GitHub CLI", "云端发布工具")
        .replace("gh auth login", "云端工具登录")
    )


def _has_changes(root: Path, runner: Runner) -> bool:
    return bool(_git(root, ["status", "--short"], runner))


def _git(root: Path, args: list[str], runner: Runner) -> str:
    result = runner(root, ["git", *args])
    return result.stdout.strip() if result.returncode == 0 else ""


def _write_release_notes(root: Path, tag: str, runner: Runner) -> Path:
    notes_dir = root / ".ai" / "release"
    notes_dir.mkdir(parents=True, exist_ok=True)
    path = notes_dir / f"{tag}.md"
    previous_tag = _previous_release_tag(root, tag, runner)
    commits = _release_commits(root, tag, previous_tag, runner)
    body = _render_release_notes(tag, previous_tag, commits, root / "CHANGELOG.md")
    path.write_text(body, encoding="utf-8")
    return path


def _previous_release_tag(root: Path, tag: str, runner: Runner) -> str | None:
    tags = _git(root, ["tag", "--sort=-version:refname"], runner).splitlines()
    for candidate in tags:
        candidate = candidate.strip()
        if candidate and candidate != tag and _tag_to_pep440_version(candidate):
            return candidate
    return None


def _release_commits(root: Path, tag: str, previous_tag: str | None, runner: Runner) -> list[str]:
    revision = f"{previous_tag}..HEAD" if previous_tag else "HEAD"
    result = runner(root, ["git", "log", "--pretty=format:%h %s", revision])
    if result.returncode != 0:
        return []
    release_commit_subject = f"chore: prepare release {tag}"
    commits = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        _, _, subject = line.partition(" ")
        if subject == release_commit_subject:
            continue
        commits.append(line)
    return commits


def _render_release_notes(tag: str, previous_tag: str | None, commits: list[str], changelog: Path) -> str:
    lines = [f"# {tag}", ""]
    if previous_tag:
        lines.extend([f"## Changes since {previous_tag}", ""])
    else:
        lines.extend(["## Changes", ""])

    if commits:
        lines.extend([f"- {commit}" for commit in commits])
    else:
        lines.append("- No code changes detected since the previous release tag.")

    if changelog.exists():
        lines.extend(["", "## Project Changelog", "", _latest_changelog_section(changelog.read_text(encoding="utf-8")).strip()])
    lines.append("")
    return "\n".join(lines)


def _latest_changelog_section(text: str) -> str:
    match = re.search(r"^## .+?(?=^## |\Z)", text, flags=re.MULTILINE | re.DOTALL)
    return match.group(0) if match else text.strip()


def _command_error(label: str, result: subprocess.CompletedProcess[str]) -> str:
    detail = (result.stderr or result.stdout).strip()
    return f"{label} 失败：{detail}" if detail else f"{label} 失败。"


def _run(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
