from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from project_copilot.workflow.sync_project_state import sync_project_state
from project_copilot.workflow.types import WorkflowContext, WorkflowResult

Runner = Callable[[Path, list[str]], subprocess.CompletedProcess[str]]

TAG_RE = re.compile(r"\bv?\d+\.\d+\.\d+(?:[-.][0-9A-Za-z.-]+)?\b")


@dataclass
class ReleaseOutcome:
    tag: str
    status: str
    actions: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    release_notes: Path | None = None


def run(context: WorkflowContext) -> WorkflowResult:
    tag = extract_tag(context.text)
    if not tag:
        return WorkflowResult(
            intent_name=context.intent_name,
            status="blocked",
            title="发布被阻止。",
            summary="请提供明确版本标签，例如：project-copilot 发布 v0.3.0-alpha.2",
            next_steps=["输入 `project-copilot 发布 v0.3.0-alpha.2`。"],
        )

    outcome = release_project(context.root, tag)
    return WorkflowResult(
        intent_name=context.intent_name,
        status=outcome.status,
        title="发布完成。" if outcome.status == "success" else "发布被阻止。",
        summary=f"目标标签：{outcome.tag}",
        details={
            "已执行": outcome.actions,
            "阻塞项": outcome.blockers,
            "Release notes": str(outcome.release_notes) if outcome.release_notes else None,
        },
        next_steps=[] if outcome.status == "success" else ["修复阻塞项后重新运行发布命令。"],
    )


def release_project(root: Path, tag: str, runner: Runner | None = None) -> ReleaseOutcome:
    runner = runner or _run
    outcome = ReleaseOutcome(tag=tag, status="blocked")
    blockers = _preflight(root, tag, runner)
    if blockers:
        outcome.blockers.extend(blockers)
        return outcome

    sync = sync_project_state(root)
    if sync.updated_files:
        outcome.actions.append("同步项目状态")

    test = runner(root, ["pytest", "-q"])
    if test.returncode != 0:
        outcome.blockers.append("测试失败：pytest -q")
        return outcome
    outcome.actions.append("pytest -q")

    notes = _write_release_notes(root, tag)
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
    outcome.status = "success"
    return outcome


def extract_tag(text: str) -> str | None:
    match = TAG_RE.search(text)
    return match.group(0) if match else None


def _preflight(root: Path, tag: str, runner: Runner) -> list[str]:
    blockers: list[str] = []
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
    elif runner(root, ["gh", "auth", "status"]).returncode != 0:
        blockers.append("GitHub CLI 未登录，请先运行 gh auth login。")
    return blockers


def _has_changes(root: Path, runner: Runner) -> bool:
    return bool(_git(root, ["status", "--short"], runner))


def _git(root: Path, args: list[str], runner: Runner) -> str:
    result = runner(root, ["git", *args])
    return result.stdout.strip() if result.returncode == 0 else ""


def _write_release_notes(root: Path, tag: str) -> Path:
    notes_dir = root / ".ai" / "release"
    notes_dir.mkdir(parents=True, exist_ok=True)
    path = notes_dir / f"{tag}.md"
    changelog = root / "CHANGELOG.md"
    body = changelog.read_text(encoding="utf-8") if changelog.exists() else "# Release Notes\n"
    path.write_text(f"# {tag}\n\n{body}", encoding="utf-8")
    return path


def _command_error(label: str, result: subprocess.CompletedProcess[str]) -> str:
    detail = (result.stderr or result.stdout).strip()
    return f"{label} 失败：{detail}" if detail else f"{label} 失败。"


def _run(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
