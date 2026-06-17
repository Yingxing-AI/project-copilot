from __future__ import annotations

from datetime import datetime

from project_copilot.gitops import init_git_if_needed
from project_copilot.memory import MemoryStore
from project_copilot.workflow.codex_native import ensure_codex_native_files
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


def run(context: WorkflowContext) -> WorkflowResult:
    root = context.root
    root.mkdir(parents=True, exist_ok=True)
    memory = MemoryStore(root)
    created: list[str] = []
    defaults = {
        "README.md": "# Project\n\n由 Codex 负责开发，由 Project Copilot 记录项目历史和关键决策。\n",
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
    project_context = build_project_context(
        project_name=root.name,
        project_description=_extract_description(context.text),
        target_users="待确认",
        mvp="待确认",
    )
    context_path = memory.ai_dir / "PROJECT_CONTEXT.md"
    if _is_placeholder_context(context_path.read_text(encoding="utf-8")):
        context_path.write_text(project_context, encoding="utf-8")
    git_initialized = init_git_if_needed(root)
    memory.append_memory(f"收到初始化意图：{context.text.strip()}")

    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已完成项目档案初始化。",
        summary="我已经准备好项目档案、状态记录、路线图、决策记录、工作日志和知识库。",
        details={
            "创建文件": created,
            "保存进度记录": "已建立" if git_initialized else "已存在或暂不可用",
        },
        next_steps=["打开 Codex：codex", "对 Codex 说“继续开发这个项目”。"],
    )


def build_project_context(project_name: str, project_description: str, target_users: str, mvp: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    return "\n".join(
        [
            "# Project Context",
            "",
            f"项目名称：{project_name}",
            "",
            f"项目使命：{project_description or '待确认。'}",
            "",
            f"目标用户：{target_users or '待确认。'}",
            "",
            "商业目标：待确认。",
            "",
            f"MVP 范围：{mvp or '待确认。'}",
            "",
            "技术栈：待确认。",
            "",
            "说明：这里记录长期稳定背景，极少修改；不要写临时状态。",
            "",
            f"创建日期：{today}",
            "",
        ]
    )


def _extract_description(text: str) -> str:
    cleaned = text.strip()
    for phrase in ("请初始化项目", "初始化项目", "初始化", "开始一个新项目"):
        cleaned = cleaned.replace(phrase, "")
    cleaned = cleaned.strip(" ，,。")
    return cleaned


def _is_placeholder_context(text: str) -> bool:
    return "待确认" in text or "待补充" in text
