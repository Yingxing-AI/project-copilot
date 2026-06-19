from __future__ import annotations

from project_copilot.memory import MemoryStore
from project_copilot.workflow.codex_native import ensure_codex_native_files
from project_copilot.workflow.project_proposal import (
    ProjectProposal,
    build_project_charter,
    build_decisions,
    build_project_context,
    build_roadmap,
    build_status,
    parse_project_proposal,
    project_proposal_prompt,
)
from project_copilot.validation.report import refresh_validation_report as refresh_validation_report_file
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    root = context.root
    root.mkdir(parents=True, exist_ok=True)
    memory = MemoryStore(root)
    created: list[str] = []
    defaults = {
        "README.md": "# Project\n\n由 Codex 负责开发，由 Git 负责版本管理，由 Project Copilot 记录项目记忆和关键决策原因。\n",
        "LICENSE": "MIT License\n\nCopyright (c) 2026 Project Copilot Contributors\n",
    }
    for name, content in defaults.items():
        path = root / name
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            created.append(name)

    docs = root / "docs"
    if not docs.exists():
        docs.mkdir()
        created.append("docs/")

    created.extend(str(path.relative_to(root)) for path in memory.ensure())
    created.extend(str(path.relative_to(root)) for path in ensure_codex_native_files(root))
    proposal = parse_project_proposal(context.text, root.name)
    created.extend(_write_initial_memory(memory, proposal))
    memory.append_memory("完成首次方案驱动项目档案初始化。")
    validation_report_path, _ = refresh_validation_report_file(root)

    status = "success"
    title = "已完成项目档案初始化。"
    summary = "我已经根据项目方案生成了项目记忆、状态、路线图和决策记录。"
    if proposal.missing_fields:
        status = "needs_input"
        title = "项目方案还需要补充。"
        summary = "我先根据已给内容完成初始化，缺失项仍需要你补充。"

    return WorkflowResult(
        intent_name=context.intent_name,
        status=status,
        title=title,
        summary=summary,
        details={
            "创建文件": created,
            "验证汇总": str(validation_report_path.relative_to(root)) if validation_report_path.is_relative_to(root) else str(validation_report_path),
            "已识别项目使命": proposal.mission or "未识别",
            "已识别目标用户": proposal.target_users or "未识别",
            "已识别商业目标": proposal.business_goal or "未识别",
            "已识别 MVP 范围": proposal.mvp_scope or "未识别",
            "已识别技术栈": proposal.tech_stack or "未识别",
            "当前阶段": proposal.current_stage or "方案确认中",
            "初始 Roadmap": list(proposal.roadmap_items) or ["待补充"],
            "初始 Decisions": list(proposal.decision_items) or ["待补充"],
            "待补充信息": list(proposal.missing_fields),
        },
        next_steps=_next_steps(proposal),
    )


def _write_initial_memory(memory: MemoryStore, proposal: ProjectProposal) -> list[str]:
    charter_path = memory.ai_dir / "PROJECT_CHARTER.md"
    context_path = memory.ai_dir / "PROJECT_CONTEXT.md"
    status_path = memory.ai_dir / "STATUS.md"
    roadmap_path = memory.ai_dir / "ROADMAP.md"
    decisions_path = memory.ai_dir / "DECISIONS.md"
    charter_path.write_text(build_project_charter(memory.root.name, proposal), encoding="utf-8")
    context_path.write_text(build_project_context(memory.root.name, proposal), encoding="utf-8")
    status_path.write_text(build_status(memory.root.name, proposal), encoding="utf-8")
    roadmap_path.write_text(build_roadmap(proposal), encoding="utf-8")
    decisions_path.write_text(build_decisions(proposal), encoding="utf-8")
    return [
        ".ai/PROJECT_CHARTER.md",
        ".ai/PROJECT_CONTEXT.md",
        ".ai/STATUS.md",
        ".ai/ROADMAP.md",
        ".ai/DECISIONS.md",
    ]


def _next_steps(proposal: ProjectProposal) -> list[str]:
    steps = ["打开 Codex：codex", "对 Codex 说“继续开发这个项目”。"]
    if proposal.missing_fields:
        steps.insert(0, project_proposal_prompt(proposal.missing_fields))
    return steps
