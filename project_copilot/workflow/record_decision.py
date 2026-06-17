from __future__ import annotations

from datetime import datetime

from project_copilot.memory import MemoryStore
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

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    path = memory.ai_dir / "DECISIONS.md"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n## {stamp}\n\n")
        handle.write(f"- 决策：{decision}\n")
        handle.write("- 原因：待补充。\n")
        handle.write("- 影响：后续需求以此为边界。\n")
    memory.append_memory(f"记录关键决策：{decision}")
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已记录决策。",
        summary=decision,
        next_steps=["后续如方向变化，先运行“项目偏航检查”。"],
    )


def _extract_decision(text: str) -> str:
    cleaned = text.strip()
    for phrase in ("记录决策", "保存决策", "新增决策", "decision"):
        cleaned = cleaned.replace(phrase, "")
    return cleaned.strip(" ：:,，。")
