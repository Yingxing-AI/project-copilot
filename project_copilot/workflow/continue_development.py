from __future__ import annotations

from pathlib import Path

from project_copilot.analyzer import analyze_project
from project_copilot.memory import MemoryStore
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    if not _memory_layer_installed(context.root):
        return WorkflowResult(
            intent_name=context.intent_name,
            status="needs_input",
            title="尚未安装项目记忆层。",
            summary="continue_development 是只读恢复入口，不会自动创建 `.ai`、目录或模板。",
            details={
                "项目根目录": str(context.root),
            },
            next_steps=["请先运行 `project-copilot adopt` 接管已有项目，或运行“接管这个已有项目”。"],
        )

    memory = MemoryStore(context.root)
    charter_text = memory.read("PROJECT_CHARTER.md").strip() or memory.read("PROJECT_CONTEXT.md").strip()
    status_text = memory.read("STATUS.md").strip()
    hypotheses_text = memory.read("HYPOTHESES.md").strip()
    session_text = _read_optional(context.root / ".ai" / "sessions" / "current.md").strip()
    analysis = analyze_project(context.root)
    next_step = _resume_step(hypotheses_text)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已恢复当前上下文。",
        summary=f"当前阶段：{analysis.stage}",
        details={
            "PROJECT_CHARTER 摘要": _summarize_status(charter_text),
            "STATUS 摘要": _summarize_status(status_text),
            "HYPOTHESES 摘要": _summarize_status(hypotheses_text) if hypotheses_text else "暂无 HYPOTHESES.md 内容。",
            "Session 候选": _summarize_status(session_text),
        },
        next_steps=[next_step],
    )


def _summarize_status(status_text: str) -> str:
    lines = [line.strip() for line in status_text.splitlines() if line.strip()]
    return "；".join(lines[:5]) if lines else "暂无 STATUS.md 内容。"


def _resume_step(hypotheses_text: str) -> str:
    if hypotheses_text.strip():
        return "优先确认未验证内容，再继续当前任务。"
    return "继续当前任务，不新增规划。"


def _memory_layer_installed(root: Path) -> bool:
    ai_dir = root / ".ai"
    if not ai_dir.is_dir():
        return False
    if not ((ai_dir / "PROJECT_CHARTER.md").exists() or (ai_dir / "PROJECT_CONTEXT.md").exists()):
        return False
    return (ai_dir / "STATUS.md").exists()


def _read_optional(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")
