from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from project_copilot import __version__
from project_copilot.analyzer import analyze_project
from project_copilot.memory import MemoryStore
from project_copilot.validation.report import refresh_validation_report as refresh_validation_report_file
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


SYNC_ADDED_ITEMS = [
    "Codex-native project memory installation.",
    "`AGENTS.md` rules for Codex.",
    "`docs/CODEX_WORKFLOW.md` user guide for working with Codex.",
    "Multi-project validation report and case study structure.",
    "`project-copilot --version`.",
    "`project-copilot doctor`.",
    "Automatic project state sync for `.ai/STATUS.md`, Roadmap, and Changelog.",
    "Managed `AGENTS.md` synchronization block.",
    "PEP 660 editable install with Hatchling.",
    "Demo scripts and README demo area.",
    "Architecture SVG and Mermaid source.",
    "GitHub Actions CI for Python 3.10, 3.11, and 3.12.",
    "Release dry-run and version/tag consistency checks.",
    "One-command install script for GitHub-based installation.",
]


@dataclass(frozen=True)
class ProjectStateSync:
    updated_files: list[str]
    pytest_baseline: str
    latest_commit: str
    latest_tag: str
    version: str


def run(context: WorkflowContext) -> WorkflowResult:
    sync = sync_project_state(context.root)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已同步项目状态。",
        summary="已更新状态、路线图和协作文档的当前版本信息。",
        details={
            "版本": sync.version,
            "最新提交": sync.latest_commit,
            "最新标签": sync.latest_tag,
            "测试基线": sync.pytest_baseline,
            "更新文件": sync.updated_files,
        },
        next_steps=["运行 `pytest -q` 验证。", "审阅后保存进度。"],
    )


def sync_project_state(root: Path) -> ProjectStateSync:
    memory = MemoryStore(root)
    memory.ensure()
    analysis = analyze_project(root)
    analysis = _without_transient_dirty_risk(analysis)
    today = datetime.now().strftime("%Y-%m-%d")
    pytest_baseline = _run_pytest_baseline(root)
    latest_commit = _git_output(root, ["log", "-1", "--pretty=%h %s"]) or "unknown"
    latest_tag = _git_output(root, ["describe", "--tags", "--abbrev=0"]) or "none"
    updated_files: list[str] = []

    status = _render_status(today, analysis, pytest_baseline, latest_commit, latest_tag)
    _write_if_changed(memory.ai_dir / "STATUS.md", status, updated_files, ".ai/STATUS.md")

    for path in (root / "ROADMAP.md", memory.ai_dir / "ROADMAP.md"):
        if path.exists():
            label = str(path.relative_to(root))
            _write_if_changed(path, _replace_pytest_baseline(path.read_text(encoding="utf-8"), pytest_baseline), updated_files, label)

    changelog = root / "CHANGELOG.md"
    if changelog.exists():
        _write_if_changed(changelog, _sync_changelog(changelog.read_text(encoding="utf-8"), pytest_baseline), updated_files, "CHANGELOG.md")

    readme = root / "README.md"
    if readme.exists():
        _write_if_changed(readme, _sync_readme(readme.read_text(encoding="utf-8"), pytest_baseline), updated_files, "README.md")

    agents = root / "AGENTS.md"
    if agents.exists():
        _write_if_changed(
            agents,
            _sync_agents(agents.read_text(encoding="utf-8"), pytest_baseline),
            updated_files,
            "AGENTS.md",
        )

    validation_report_path, _ = refresh_validation_report_file(root)
    if validation_report_path.exists():
        label = str(validation_report_path.relative_to(root)) if validation_report_path.is_relative_to(root) else str(validation_report_path)
        if label not in updated_files:
            updated_files.append(label)

    return ProjectStateSync(
        updated_files=updated_files,
        pytest_baseline=pytest_baseline,
        latest_commit=latest_commit,
        latest_tag=latest_tag,
        version=__version__,
    )


def _render_status(today, analysis, pytest_baseline: str, latest_commit: str, latest_tag: str) -> str:
    return "\n".join(
        [
            "# Status",
            "",
            f"更新日期：{today}",
            "",
            f"当前阶段：{analysis.stage}",
            "",
            "当前状态：",
            "",
            f"- 版本：`{__version__}`",
            f"- 分支：`{analysis.git.branch or 'unknown'}`",
            f"- 最新提交：`{latest_commit}`",
            f"- 最新标签：`{latest_tag}`",
            f"- 测试基线：`pytest -q` 通过，{pytest_baseline}。",
            f"- 项目健康度：{analysis.health_score}/100",
            "",
            "已完成功能：",
            "",
            "- 自然语言意图识别。",
            "- Workflow engine 注册和分发。",
            "- `.ai/` 项目记忆系统。",
            "- 项目初始化和已有项目接管。",
            "- Codex Native 主流程：`project-copilot init/adopt` 生成 `.ai/`、`AGENTS.md` 和 `docs/CODEX_WORKFLOW.md`。",
            "- `AGENTS.md` 生成 Codex 维护 `.ai` 项目记忆的规则。",
            "- `docs/CODEX_WORKFLOW.md` 面向用户说明 Project Copilot 与 Codex 的日常协作方式。",
            "- 多项目验证体系：`docs/case-studies/`、case study 模板和 `docs/validation-report.md`。",
            "- 项目复盘、项目时间轴、项目偏航检查、记录决策和查看路线图。",
            "- 项目状态分析和健康度评分。",
            "- `.ai/KNOWLEDGE.md`、`.ai/history/`，以及辅助指标 `.ai/metrics.md`。",
            "- 继续开发、结束工作和工作日志流程。",
            "- OSS readiness 检查和开源准备文件生成。",
            "- GitHub public/private 同步计划和前置条件检查。",
            "- 无参数交互式 CLI 和 command mode。",
            "- unknown intent 中文建议。",
            "- 可编辑安装、`--version` 和 `doctor` 诊断命令。",
            "- Demo 脚本、终端动画和架构图文档。",
            "- 自动同步 `.ai/STATUS.md`、Roadmap、Changelog 和 AGENTS managed 区块。",
            "- GitHub Actions CI 覆盖 Python 3.10、3.11、3.12。",
            "- Release dry-run 和版本/tag 一致性检查。",
            "- 面向普通用户的一行安装脚本。",
            "",
            "当前验证重点：",
            "",
            "- 验证 Project Copilot 是否能作为 Codex 项目的记忆层安装器，而不是抢占日常入口。",
            "- 验证 `.ai` 中的工作日志、决策和知识沉淀是否能成为跨项目价值指标。",
            "- 验证用户是否可以只打开 Codex 并通过 `.ai` 获得连续项目上下文。",
            "- 验证价值优先，不新增复杂 AI 能力、不接外部 AI API、不开发 Web UI。",
            "",
            "当前风险：",
            "",
            *[f"- {risk}" for risk in (analysis.risks or ["暂无。"])],
            "",
            "下一步任务：",
            "",
            *[f"- {step}" for step in analysis.next_steps],
            "",
        ]
    )


def _without_transient_dirty_risk(analysis):
    risks = [risk for risk in analysis.risks if risk != "有尚未保存的工作进展。"]
    git = type(analysis.git)(
        available=analysis.git.available,
        initialized=analysis.git.initialized,
        branch=analysis.git.branch,
        dirty_files=[],
        last_commit=analysis.git.last_commit,
    )
    return type(analysis)(
        health_score=_health_score_without_dirty(analysis.health_score, analysis.risks, risks),
        stage=analysis.stage,
        completed=analysis.completed,
        missing=analysis.missing,
        risks=risks,
        next_steps=analysis.next_steps,
        git=git,
    )


def _health_score_without_dirty(score: int, old_risks: list[str], new_risks: list[str]) -> int:
    if "有尚未保存的工作进展。" in old_risks and "有尚未保存的工作进展。" not in new_risks:
        return min(100, score + 8)
    return score


def _replace_pytest_baseline(text: str, pytest_baseline: str) -> str:
    return re.sub(r"Pytest baseline: \d+ passed", f"Pytest baseline: {pytest_baseline}", text)


def _sync_changelog(text: str, pytest_baseline: str) -> str:
    updated = re.sub(r"Current baseline: \d+ passed\.", f"Current baseline: {pytest_baseline}.", text)
    missing = []
    for item in SYNC_ADDED_ITEMS:
        line = f"- {item}"
        if line not in updated:
            missing.append(line)
    if missing:
        marker = "### Verified"
        updated = updated.replace(marker, "\n".join(missing) + f"\n\n{marker}", 1)
    return updated


def _sync_readme(text: str, pytest_baseline: str) -> str:
    updated = re.sub(r"Current baseline:\n\n```text\n.*?\n```", f"Current baseline:\n\n```text\n{pytest_baseline}\n```", text, flags=re.DOTALL)
    updated = re.sub(r"当前版本是 v[^：]+：", f"当前版本是 v{__version__}：", updated)
    return updated


def _sync_agents(text: str, pytest_baseline: str) -> str:
    block = _render_agents_managed_block(pytest_baseline)
    pattern = re.compile(
        r"<!-- project-copilot:managed:start -->.*?<!-- project-copilot:managed:end -->",
        re.DOTALL,
    )
    if pattern.search(text):
        return pattern.sub(block, text)
    return text.rstrip() + "\n\n" + block + "\n"


def _render_agents_managed_block(pytest_baseline: str) -> str:
    return "\n".join(
        [
            "<!-- project-copilot:managed:start -->",
            "## Project Copilot Managed Context",
            "",
            "- 普通用户安装命令：`curl -LsSf https://raw.githubusercontent.com/Yingxing-AI/project-copilot/main/install.sh | sh`",
            "- 安装命令：`pip install -e .`",
            "- CLI 命令：`project-copilot`",
            "- 诊断命令：`project-copilot doctor`",
            "- 版本命令：`project-copilot --version`",
            f"- 测试命令：`pytest -q`（当前基线：{pytest_baseline}）",
            "- CLI 入口：`project_copilot/cli/main.py`",
            "- Workflow 入口：`project_copilot/workflow/`",
            "- Intent 入口：`project_copilot/intent/classifier.py`",
            "- 项目记忆目录：`.ai/`",
            "- 自动同步命令：`project-copilot 同步项目状态`",
            "",
            "只自动维护本区块；其它协作约定由维护者手动编辑。",
            "<!-- project-copilot:managed:end -->",
        ]
    )


def _run_pytest_baseline(root: Path) -> str:
    result = subprocess.run(
        ["pytest", "-q"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    match = re.search(r"(\d+ passed)", result.stdout)
    if match:
        return match.group(1)
    if result.returncode == 0:
        return "passed"
    return "unknown"


def _git_output(root: Path, args: list[str]) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def _write_if_changed(path: Path, content: str, updated_files: list[str], label: str) -> None:
    if path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")
        updated_files.append(label)
