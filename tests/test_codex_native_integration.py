from pathlib import Path

from project_copilot.workflow import run_structured_workflow


def test_adopt_generates_agents_md(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Existing\n", encoding="utf-8")

    result = run_structured_workflow(tmp_path, "adopt")

    agents = tmp_path / "AGENTS.md"
    assert result.intent_name == "adopt_project"
    assert result.status == "success"
    assert agents.exists()
    assert "你是 Codex。" in agents.read_text(encoding="utf-8")


def test_init_generates_codex_workflow_doc(tmp_path: Path) -> None:
    result = run_structured_workflow(tmp_path, "init")

    workflow_doc = tmp_path / "docs" / "CODEX_WORKFLOW.md"
    assert result.intent_name == "init_project"
    assert result.status == "success"
    assert workflow_doc.exists()
    text = workflow_doc.read_text(encoding="utf-8")
    assert "每天开始" in text
    assert "codex" in text
    assert "继续开发这个项目" in text


def test_ai_memory_structure(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "init")

    ai_dir = tmp_path / ".ai"
    for name in (
        "PROJECT_CONTEXT.md",
        "STATUS.md",
        "ROADMAP.md",
        "MEMORY.md",
        "DECISIONS.md",
        "WORKLOG.md",
        "KNOWLEDGE.md",
        "metrics.md",
    ):
        assert (ai_dir / name).exists()
    assert (ai_dir / "history").is_dir()

    context = (ai_dir / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")
    assert "项目使命：" in context
    assert "目标用户：" in context
    assert "商业目标：" in context
    assert "MVP 范围：" in context
    assert "技术栈：" in context


def test_agents_md_contains_codex_rules(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "init")

    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "你负责开发。" in text
    assert "同时你必须维护 `.ai` 项目记忆。" in text
    assert "阅读 `.ai/PROJECT_CONTEXT.md`" in text
    assert "更新 `.ai/STATUS.md`" in text
    assert "追加 `.ai/WORKLOG.md`" in text
    assert "不要覆盖历史决策" in text
    assert "不要未经用户确认扩大 MVP 范围" in text
    assert "`commit` = 保存进度" in text
    assert "`push` = 备份到云端" in text
    assert "`release` = 发布版本" in text
    assert "`tag` = 版本标记" in text


def test_readme_promotes_codex_native_flow() -> None:
    text = Path("README.md").read_text(encoding="utf-8")

    assert "Project Copilot installs a persistent project memory layer for Codex." in text
    assert "project-copilot adopt" in text
    assert "project-copilot init" in text
    assert "codex" in text
    assert "用户只和 Codex 对话" in text


def test_interactive_mode_not_primary() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    usage = Path("docs/USAGE.md").read_text(encoding="utf-8")

    assert "Interactive mode is kept for compatibility" in readme
    assert "not the primary daily workflow" in readme
    assert "Prefer `project-copilot adopt` or `project-copilot init`, then `codex`." in usage
