from __future__ import annotations

from datetime import datetime

from project_copilot.memory import MemoryStore
from project_copilot.workflow.codex_native import ensure_codex_native_files
from project_copilot.workflow.project_proposal import (
    ProjectProposal,
    build_project_charter,
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
    decisions_path.write_text(
        "# Decisions\n\n说明：旧版决策索引。初始化阶段的确认决策已写入 `.ai/adr/`；本文件只保留兼容摘要。\n",
        encoding="utf-8",
    )
    written = [
        ".ai/PROJECT_CHARTER.md",
        ".ai/PROJECT_CONTEXT.md",
        ".ai/STATUS.md",
        ".ai/ROADMAP.md",
        ".ai/DECISIONS.md",
    ]
    written.extend(_write_initial_adrs(memory, proposal))
    return written


def _write_initial_adrs(memory: MemoryStore, proposal: ProjectProposal) -> list[str]:
    adr_dir = memory.ai_dir / "adr"
    written: list[str] = []
    today = datetime.now().strftime("%Y-%m-%d")
    existing_titles = _existing_adr_titles(adr_dir)
    existing_numbers = [
        int(path.name.split("-", 1)[0])
        for path in adr_dir.glob("*.md")
        if path.name != "index.md" and path.name[:4].isdigit()
    ]
    next_number = max(existing_numbers, default=0) + 1

    for item in proposal.decision_items:
        decision, reason, impact = _split_decision(item)
        if decision in existing_titles:
            continue
        filename = f"{next_number:04d}-{_slugify(decision)}.md"
        path = adr_dir / filename
        path.write_text(
            "\n".join(
                [
                    f"# ADR {next_number:04d}: {decision}",
                    "",
                    f"日期：{today}",
                    "",
                    "状态：Accepted",
                    "",
                    "背景：",
                    "",
                    "本 ADR 由初始化阶段识别出的确认决策生成。",
                    "",
                    "决策：",
                    "",
                    decision,
                    "",
                    "原因：",
                    "",
                    reason,
                    "",
                    "取舍：",
                    "",
                    "待补充。",
                    "",
                    "影响：",
                    "",
                    impact,
                    "",
                ]
            ),
            encoding="utf-8",
        )
        _append_adr_index(adr_dir / "index.md", next_number, decision, filename)
        written.append(f".ai/adr/{filename}")
        existing_titles.add(decision)
        next_number += 1
    return written


def _next_steps(proposal: ProjectProposal) -> list[str]:
    steps = ["打开 Codex：codex", "对 Codex 说“继续开发这个项目”。"]
    if proposal.missing_fields:
        steps.insert(0, project_proposal_prompt(proposal.missing_fields))
    return steps


def _split_decision(text: str) -> tuple[str, str, str]:
    cleaned = text.strip().strip("。；;")
    if not cleaned:
        return "待补充。", "待补充。", "待补充。"

    decision = cleaned
    reason = "待补充。"
    impact = "待补充。"
    for separator in ("因为", "由于", "原因是"):
        if separator in cleaned:
            left, right = cleaned.split(separator, 1)
            decision = left.strip(" ，,。；;")
            reason = right.strip(" ，,。；;") or reason
            break
    if "影响" in cleaned:
        parts = cleaned.split("影响：", 1) if "影响：" in cleaned else cleaned.split("影响:", 1)
        if len(parts) == 2:
            impact = parts[1].strip(" ，,。；;") or impact
    return decision or "待补充。", reason, impact


def _slugify(text: str) -> str:
    chars = [char.lower() if char.isascii() and char.isalnum() else "-" for char in text]
    slug = "".join(chars)
    parts = [part for part in slug.split("-") if part]
    return "-".join(parts[:6]) if parts else "decision"


def _append_adr_index(index_path, number: int, decision: str, filename: str) -> None:
    line = f"- [ADR {number:04d}: {decision}]({filename})"
    text = index_path.read_text(encoding="utf-8")
    text = text.replace("\n暂无 ADR。\n", "\n").replace("暂无 ADR。\n", "")
    if line not in text:
        index_path.write_text(text.rstrip() + f"\n{line}\n", encoding="utf-8")


def _existing_adr_titles(adr_dir) -> set[str]:
    titles: set[str] = set()
    for path in adr_dir.glob("*.md"):
        if path.name == "index.md":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("# ADR ") and ": " in stripped:
                titles.add(stripped.split(": ", 1)[1].strip())
                break
    return titles
