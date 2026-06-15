from __future__ import annotations

from project_copilot.analyzer import analyze_project
from project_copilot.memory import MemoryStore
from project_copilot.workflow.types import WorkflowContext, WorkflowResult
from project_copilot.workflow.utils import as_bullets


def run(context: WorkflowContext) -> WorkflowResult:
    root = context.root
    root.mkdir(parents=True, exist_ok=True)
    memory = MemoryStore(root)
    memory.ensure()
    profile = _inspect_existing_project(root)
    analysis = analyze_project(root)

    (memory.ai_dir / "PROJECT_CONTEXT.md").write_text(
        "\n".join(
            [
                "# Project Context",
                "",
                f"项目名称：{root.name}",
                "",
                "项目是什么：基于已有文件自动接管，具体业务目标待确认。",
                "",
                "项目目标：在不覆盖现有代码和文档的前提下纳入 Project Copilot 管理。",
                "",
                "目标用户：待确认。",
                "",
                "技术栈：",
                *as_bullets(profile["tech_stack"] or ["待确认"]),
                "",
                "现有线索：",
                *as_bullets(profile["signals"] or ["未发现明显项目线索"]),
                "",
            ]
        ),
        encoding="utf-8",
    )
    (memory.ai_dir / "STATUS.md").write_text(
        "\n".join(
            [
                "# Status",
                "",
                f"当前阶段：{analysis.stage}",
                "",
                "已发现内容：",
                *as_bullets(profile["signals"] or analysis.completed),
                "",
                "缺失或待补充：",
                *as_bullets(analysis.missing),
                "",
                "下一步任务：",
                *as_bullets(analysis.next_steps),
                "",
            ]
        ),
        encoding="utf-8",
    )
    memory.append_memory(f"接管已有项目：{context.text.strip()}")

    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已接管已有项目。",
        summary="处理方式：未覆盖现有 README、LICENSE、源码或文档。",
        details={
            "已更新": [".ai/PROJECT_CONTEXT.md", ".ai/STATUS.md", ".ai/MEMORY.md"],
            "识别技术栈": profile["tech_stack"],
            "项目线索": profile["signals"][:8],
        },
        next_steps=analysis.next_steps,
    )


def _inspect_existing_project(root) -> dict[str, list[str]]:
    tech_stack: list[str] = []
    signals: list[str] = []
    markers = {
        "pyproject.toml": "Python",
        "requirements.txt": "Python",
        "package.json": "Node.js",
        "pnpm-lock.yaml": "Node.js",
        "Dockerfile": "Docker",
        "docker-compose.yml": "Docker Compose",
        "go.mod": "Go",
        "Cargo.toml": "Rust",
    }
    for marker, label in markers.items():
        if (root / marker).exists():
            if label not in tech_stack:
                tech_stack.append(label)
            signals.append(marker)

    for directory in ("src", "app", "backend", "frontend", "tests", "docs"):
        if (root / directory).exists():
            signals.append(f"{directory}/")

    for document in ("README.md", "LICENSE", "AGENTS.md", "CONTRIBUTING.md"):
        if (root / document).exists():
            signals.append(document)

    return {"tech_stack": tech_stack, "signals": signals}
