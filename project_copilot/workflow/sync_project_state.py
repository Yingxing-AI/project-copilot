from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from project_copilot.memory import MemoryStore
from project_copilot.validation.report import refresh_validation_report as refresh_validation_report_file
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


@dataclass(frozen=True)
class ProjectStateSync:
    updated_files: list[str]


def run(context: WorkflowContext) -> WorkflowResult:
    sync = sync_project_state(context.root)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已刷新派生记忆状态。",
        summary="已根据真实 `.ai` 项目记忆刷新验证报告；未运行测试，未读取 Git，未同步 Changelog。",
        details={
            "更新文件": sync.updated_files,
        },
        next_steps=["测试、Git、Commit、Push、Release 和 Changelog 由 Codex/Git 负责。"],
    )


def sync_project_state(root: Path) -> ProjectStateSync:
    memory = MemoryStore(root)
    memory.ensure()
    validation_report_path, _ = refresh_validation_report_file(root)
    updated_files: list[str] = []
    if validation_report_path.exists():
        label = str(validation_report_path.relative_to(root)) if validation_report_path.is_relative_to(root) else str(validation_report_path)
        updated_files.append(label)
    snapshot = memory.ai_dir / "validation.json"
    if snapshot.exists():
        updated_files.append(str(snapshot.relative_to(root)))
    return ProjectStateSync(updated_files=updated_files)
