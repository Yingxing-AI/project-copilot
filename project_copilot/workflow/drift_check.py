from __future__ import annotations

from project_copilot.memory import MemoryStore
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


EXPANSION_WORDS = ("商城", "社交", "直播", "游戏", "支付", "短视频", "外卖", "区块链", "nft")


def run(context: WorkflowContext) -> WorkflowResult:
    memory = MemoryStore(context.root)
    memory.ensure()
    project_context = memory.read("PROJECT_CONTEXT.md")
    requested = _extract_requested_change(context.text)
    warnings = _detect_drift(project_context, requested)

    if warnings:
        summary = "\n".join(
            [
                "提醒：",
                "",
                "当前项目目标：",
                _compact_context(project_context),
                "",
                "新增内容：",
                requested or context.text.strip(),
                "",
                "可能不在 MVP 范围内。",
                "",
                "请选择：",
                "1. 加入未来版本",
                "2. 修改项目目标",
                "3. 暂不处理",
            ]
        )
    else:
        summary = "当前输入没有发现明显偏离 MVP 的信号。"

    return WorkflowResult(
        intent_name=context.intent_name,
        status="needs_input" if warnings else "success",
        title="项目偏航检查",
        summary=summary,
        details={"提醒依据": warnings},
        next_steps=["如需改变方向，请先运行“记录决策 ...”。"] if warnings else ["继续按路线图推进。"],
    )


def _extract_requested_change(text: str) -> str:
    cleaned = text.strip()
    for phrase in ("项目偏航检查", "偏航检查", "检查偏航", "是否跑偏"):
        cleaned = cleaned.replace(phrase, "")
    return cleaned.strip(" ，,。")


def _detect_drift(project_context: str, requested: str) -> list[str]:
    if not requested:
        return []
    context_lower = project_context.lower()
    requested_lower = requested.lower()
    warnings = []
    for word in EXPANSION_WORDS:
        if word.lower() in requested_lower and word.lower() not in context_lower:
            warnings.append(f"“{word}”未出现在当前项目目标或 MVP 中。")
    return warnings


def _compact_context(project_context: str) -> str:
    for line in project_context.splitlines():
        if line.startswith("项目是什么："):
            return line.split("：", 1)[1].strip()
    return "暂无明确项目目标。"
