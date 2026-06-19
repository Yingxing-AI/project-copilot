from __future__ import annotations

from project_copilot.analyzer import analyze_project
from project_copilot.memory import MemoryStore
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    memory = MemoryStore(context.root)
    memory.ensure()
    analysis = analyze_project(context.root)
    candidates = memory.read_session_candidates().strip()
    return WorkflowResult(
        intent_name=context.intent_name,
        status="needs_input",
        title="已进入收工确认。",
        summary="Session Memory 模式不会自动扩写项目文件。请确认哪些候选事件值得写入长期记忆。",
        details={
            "当前开发阶段": analysis.stage,
            "当前风险": analysis.risks,
            "候选事件": candidates,
        },
        next_steps=[
            "保留三个月后仍重要的 ADR、里程碑、风险或知识。",
            "普通代码修改、测试增加和小型 Bug 修复交给 Git，不写入 `.ai`。",
            "确认后再写入 `.ai/adr/`、`.ai/MEMORY.md`、`.ai/KNOWLEDGE.md` 或 session archive。",
        ],
    )
