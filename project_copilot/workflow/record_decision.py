from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from project_copilot.memory import MemoryStore
from project_copilot.workflow.hypothesis_utils import looks_uncertain
from project_copilot.validation.report import refresh_validation_report as refresh_validation_report_file
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    memory = MemoryStore(context.root)
    memory.ensure()
    decision = _extract_decision(context.text)
    if not decision:
        return WorkflowResult(
            intent_name=context.intent_name,
            status="needs_input",
            title="需要补充决策内容。",
            summary="请用“记录决策 决定内容，因为原因”这样的方式告诉我。",
            next_steps=["例如：记录决策 MVP 先做简历导入，因为这是核心使用路径。"],
        )

    if looks_uncertain(decision):
        memory.append_session_candidate("待确认决策", decision)
        return WorkflowResult(
            intent_name=context.intent_name,
            status="needs_input",
            title="这更像一个假设，还不能写入决策。",
            summary=decision,
            next_steps=["如果已经确认，请改成明确结论后再记录决策。", "如果还未确认，保留在 Session 候选中。"],
        )

    adr_path = _write_adr(memory, decision)
    validation_report_path, _ = refresh_validation_report_file(context.root)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已记录 ADR。",
        summary=decision,
        details={
            "ADR": str(adr_path.relative_to(context.root)),
            "验证汇总": str(validation_report_path.relative_to(context.root))
            if validation_report_path.is_relative_to(context.root)
            else str(validation_report_path),
        },
        next_steps=["后续如方向变化，先运行“项目偏航检查”。"],
    )


def _extract_decision(text: str) -> str:
    cleaned = text.strip()
    for phrase in ("记录决策", "保存决策", "新增决策", "decision"):
        cleaned = cleaned.replace(phrase, "")
    return cleaned.strip(" ：:,，。")


def _write_adr(memory: MemoryStore, decision: str) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    adr_dir = memory.ai_dir / "adr"
    adr_dir.mkdir(exist_ok=True)
    number = _next_adr_number(adr_dir)
    slug = _slugify(decision)
    path = adr_dir / f"{number:04d}-{slug}.md"
    path.write_text(
        "\n".join(
            [
                f"# ADR {number:04d}: {decision}",
                "",
                f"日期：{today}",
                "",
                "状态：Accepted",
                "",
                "背景：",
                "",
                "本决策由用户通过 Project Copilot 确认记录。",
                "",
                "决策：",
                "",
                decision,
                "",
                "原因：",
                "",
                "待补充。",
                "",
                "取舍：",
                "",
                "待补充。",
                "",
                "影响：",
                "",
                "后续需求和实现应以此 ADR 为边界。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    _append_adr_index(adr_dir / "index.md", number, decision, path.name)
    return path


def _next_adr_number(adr_dir: Path) -> int:
    numbers = []
    for path in adr_dir.glob("*.md"):
        match = re.match(r"^(\d{4})-", path.name)
        if match:
            numbers.append(int(match.group(1)))
    return (max(numbers) + 1) if numbers else 1


def _slugify(text: str) -> str:
    ascii_words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    if ascii_words:
        return "-".join(ascii_words[:6])
    return "decision"


def _append_adr_index(index_path: Path, number: int, decision: str, filename: str) -> None:
    if not index_path.exists():
        index_path.write_text("# ADR Index\n\n", encoding="utf-8")
    line = f"- [ADR {number:04d}: {decision}]({filename})"
    text = index_path.read_text(encoding="utf-8")
    text = text.replace("\n暂无 ADR。\n", "\n").replace("暂无 ADR。\n", "")
    if line not in text:
        index_path.write_text(text.rstrip() + f"\n{line}\n", encoding="utf-8")
