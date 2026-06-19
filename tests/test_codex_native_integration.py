from pathlib import Path

from project_copilot.workflow.codex_native import CODEX_RULES_START, merge_agents_md, render_codex_workflow_doc
from project_copilot.workflow import run_structured_workflow


def test_adopt_generates_agents_md(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Existing\n", encoding="utf-8")

    result = run_structured_workflow(tmp_path, "adopt")

    agents = tmp_path / "AGENTS.md"
    assert result.intent_name == "adopt_project"
    assert result.status == "success"
    assert agents.exists()
    assert "你是 Codex。" in agents.read_text(encoding="utf-8")


def test_adopt_preserves_existing_agents_md(tmp_path: Path) -> None:
    existing = "# Agents\n\n- 保留项目原有协作规则。\n"
    (tmp_path / "AGENTS.md").write_text(existing, encoding="utf-8")

    run_structured_workflow(tmp_path, "adopt")

    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "- 保留项目原有协作规则。" in text
    assert CODEX_RULES_START in text
    assert "你是 Codex。" in text


def test_agents_md_merge_replaces_managed_block_only() -> None:
    first = merge_agents_md("# Agents\n\n- 手写规则。\n")
    second = merge_agents_md(first.replace("你是 Codex。", "你是旧规则。"))

    assert "- 手写规则。" in second
    assert "你是 Codex。" in second
    assert "你是旧规则。" not in second
    assert second.count(CODEX_RULES_START) == 1


def test_init_generates_codex_workflow_doc(tmp_path: Path) -> None:
    result = run_structured_workflow(tmp_path, "init")

    workflow_doc = tmp_path / "docs" / "CODEX_WORKFLOW.md"
    assert result.intent_name == "init_project"
    assert result.status == "needs_input"
    assert workflow_doc.exists()
    text = workflow_doc.read_text(encoding="utf-8")
    assert "# Project Copilot 与 Codex" in text
    assert "Git 记录代码历史。" in text
    assert "Project Copilot 记录为什么。" in text
    assert "为什么需要 Project Copilot" in text
    assert "推荐工作流" in text
    assert "codex" in text
    assert "继续开发这个项目" in text
    assert "项目秘书理念" in text


def test_codex_workflow_doc_is_user_guide_not_agent_rules(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "init")

    generated = (tmp_path / "docs" / "CODEX_WORKFLOW.md").read_text(encoding="utf-8")
    repository_doc = Path("docs/CODEX_WORKFLOW.md").read_text(encoding="utf-8")

    assert generated == repository_doc
    assert generated == render_codex_workflow_doc()
    for phrase in (
        "Codex 应",
        "Codex 将",
        "Codex should",
        "必须",
        "禁止",
        "触发条件",
        "行为规则",
    ):
        assert phrase not in generated
    assert "用户指南" not in generated
    assert "正常与 Codex 对话即可。" in generated
    assert "建议：" in generated


def test_ai_memory_structure(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "init")

    ai_dir = tmp_path / ".ai"
    for name in (
        "PROJECT_CHARTER.md",
        "PROJECT_CONTEXT.md",
        "STATUS.md",
        "HYPOTHESES.md",
        "ROADMAP.md",
        "MEMORY.md",
        "DECISIONS.md",
        "WORKLOG.md",
        "KNOWLEDGE.md",
    ):
        assert (ai_dir / name).exists()
    assert (ai_dir / "derived").is_dir()
    assert (ai_dir / "history").is_dir()
    assert (ai_dir / "adr" / "index.md").exists()
    assert (ai_dir / "sessions" / "current.md").exists()

    context = (ai_dir / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")
    assert "项目使命：" in context
    assert "目标用户：" in context
    assert "商业目标：" in context
    assert "MVP 范围：" in context
    assert "技术栈：" in context


def test_agents_md_contains_codex_rules(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "init")

    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "你的首要职责不是写代码。" in text
    assert "确保项目持续朝着既定目标演进。" in text
    assert "必须优先阻止偏离，而不是继续实现功能。" in text
    assert "你负责开发。" in text
    assert "同时你必须维护 `.ai` 分层项目记忆" in text
    assert "阅读 `.ai/PROJECT_CHARTER.md`" in text
    assert "如果旧项目没有 Charter，再读取 `.ai/PROJECT_CONTEXT.md`" in text
    assert "阅读 `.ai/adr/index.md`" in text
    assert "不自动追加 `.ai/WORKLOG.md`" in text
    assert "不要覆盖历史决策" in text
    assert "不要未经用户确认扩大 MVP 范围" in text
    assert "当前请求是否符合项目使命" in text
    assert "当前请求是否符合目标用户" in text
    assert "当前请求是否符合 MVP" in text
    assert "`commit`、`push`、`release`、`tag` 都属于 Codex/Git 工作" in text
    assert "sessions/current.md" in text


def test_agents_md_contains_guardrail_triggers(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "adopt")

    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "当用户请求超出 `.ai/PROJECT_CONTEXT.md` 的 MVP 范围时" in text
    assert "明确指出该请求超出 MVP" in text
    assert "纳入当前版本" in text
    assert "延后到未来版本" in text
    assert "取消该需求" in text
    assert "在用户选择之前，禁止直接实现。" in text
    assert "当前目标用户是谁" in text
    assert "当前需求是否匹配该用户" in text
    assert "引用 `.ai/adr/` 或 `.ai/DECISIONS.md` 中的相关决策" in text
    assert "请求用户确认是否推翻旧决策" in text


def test_agents_md_contains_memory_write_rules(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "init")

    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    for trigger in (
        "技术栈变化",
        "架构变化",
        "MVP 范围变化",
        "放弃已有功能",
        "引入重大依赖",
        "部署方式变化",
    ):
        assert trigger in text
    for field in ("日期：", "决策：", "原因：", "影响："):
        assert field in text
    assert "新的最佳实践" in text
    assert "重要设计经验" in text
    assert "开源项目启发" in text
    assert "用户反馈总结" in text
    assert "产品认知提升" in text
    assert "Session 候选规则" in text
    assert "禁止写入：" in text
    assert "代码实现细节" in text
    assert "临时调试经验" in text
    assert "`WORKLOG.md` 只保留旧版兼容和重大会话摘要" in text
    assert "普通代码修改" in text
    assert "小型 Bug 修复" in text


def test_agents_md_contains_review_triggers_and_no_fuzzy_words(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "init")

    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "连续 7 天没有重大会话摘要" in text
    assert "建议进行项目复盘" in text
    assert "连续 30 天未复盘" in text
    assert "生成项目周报或月报" in text
    assert "必要时" not in text
    assert "如果合适" not in text
    assert "可能需要" not in text


def test_repository_agents_md_is_hardened() -> None:
    text = Path("AGENTS.md").read_text(encoding="utf-8")

    assert "你的首要职责不是写代码。" in text
    assert "项目使命优先级" in text
    assert "超出 MVP" in text
    assert "与历史决策冲突" in text
    assert "Session Memory" in text
    assert "ADR" in text
    assert "必要时" not in text
    assert "如果合适" not in text
    assert "可能需要" not in text
    assert "当前基线：63 passed" in text


def test_readme_promotes_codex_native_flow() -> None:
    text = Path("README.md").read_text(encoding="utf-8")

    assert "Layered project memory for Codex." in text
    assert "project-copilot adopt" in text
    assert "project-copilot init" in text
    assert "codex" in text
    assert "用户只和 Codex 对话" in text
    assert "Session Memory" in text


def test_install_and_validation_docs_are_current() -> None:
    install = Path("install.sh").read_text(encoding="utf-8")
    contributing = Path("CONTRIBUTING.md").read_text(encoding="utf-8")
    validation = Path("docs/validation-report.md").read_text(encoding="utf-8")

    assert 'REF="${PROJECT_COPILOT_REF:-v0.3.0-beta.2}"' in install
    assert "pytest -q" in contributing
    assert "python3 -m unittest discover" not in contributing
    assert "Validation Report" in validation
    assert "自动刷新" in validation


def test_interactive_mode_not_primary() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    usage = Path("docs/USAGE.md").read_text(encoding="utf-8")

    assert "Interactive mode is kept for compatibility" in readme
    assert "not the primary daily workflow" in readme
    assert "Prefer `project-copilot adopt` or `project-copilot init`, then `codex`." in usage
