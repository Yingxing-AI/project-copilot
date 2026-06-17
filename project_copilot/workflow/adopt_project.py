from __future__ import annotations

from project_copilot.analyzer import analyze_project
from project_copilot.memory import MemoryStore
from project_copilot.workflow.codex_native import ensure_codex_native_files
from project_copilot.workflow.types import WorkflowContext, WorkflowResult
from project_copilot.workflow.utils import as_bullets


def run(context: WorkflowContext) -> WorkflowResult:
    root = context.root
    root.mkdir(parents=True, exist_ok=True)
    memory = MemoryStore(root)
    memory.ensure()
    ensure_codex_native_files(root)
    profile = _inspect_existing_project(root)
    analysis = analyze_project(root)

    (memory.ai_dir / "PROJECT_CONTEXT.md").write_text(
        "\n".join(
            [
                "# Project Context",
                "",
                f"项目名称：{root.name}",
                "",
                "项目使命：基于已有文件自动接管，具体业务目标待确认。",
                "",
                "目标用户：待确认。",
                "",
                "商业目标：待确认。",
                "",
                "MVP 范围：待确认。",
                "",
                "技术栈：",
                *as_bullets(profile["tech_stack"] or ["待确认"]),
                "",
                "说明：这里记录长期稳定背景，极少修改；不要写临时状态。",
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
    memory.append_memory("完成已有项目接管。")

    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已接管已有项目。",
        summary="处理方式：未覆盖现有 README、LICENSE 或源码；已生成 Codex 项目记忆规则。",
        details={
            "已更新": [".ai/PROJECT_CONTEXT.md", ".ai/STATUS.md", ".ai/MEMORY.md", "AGENTS.md", "docs/CODEX_WORKFLOW.md"],
            "识别技术栈": profile["tech_stack"],
            "项目线索": profile["signals"][:8],
        },
        next_steps=["打开 Codex：codex", "对 Codex 说“继续开发这个项目”。"],
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
