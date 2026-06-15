from __future__ import annotations

from project_copilot.gitops import init_git_if_needed
from project_copilot.memory import MemoryStore
from project_copilot.workflow.types import WorkflowContext


def run(context: WorkflowContext) -> str:
    root = context.root
    root.mkdir(parents=True, exist_ok=True)
    memory = MemoryStore(root)
    created: list[str] = []
    defaults = {
        "README.md": "# Project Copilot\n\n自然语言项目操作系统，面向 AI Coding 场景。\n",
        "LICENSE": "MIT License\n\nCopyright (c) 2026 Project Copilot Contributors\n",
        "AGENTS.md": "# Agents\n\n本项目由 AI Coding Agent 协作维护。优先使用中文、保持文档同步、变更前检查项目状态。\n",
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
    git_initialized = init_git_if_needed(root)
    memory.append_memory(f"收到初始化意图：{context.text.strip()}")

    lines = ["已完成项目初始化。"]
    if created:
        lines.append("创建文件：" + ", ".join(created))
    lines.append(f"Git 初始化：{'已执行' if git_initialized else '已存在或不可用'}")
    lines.append("下一步：运行“检查项目”查看健康度，或说“继续开发项目”。")
    return "\n".join(lines)
