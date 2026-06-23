from pathlib import Path

from project_copilot.memory import MemoryStore
from project_copilot.intent import classify_intent_name
from project_copilot.workflow import run_structured_workflow


def test_init_project_workflow(tmp_path: Path) -> None:
    result = run_structured_workflow(tmp_path, _sample_proposal())

    assert result.intent_name == "init_project"
    assert result.status == "success"
    assert (tmp_path / ".ai" / "PROJECT_CHARTER.md").exists()
    assert (tmp_path / ".ai" / "PROJECT_CONTEXT.md").exists()
    assert (tmp_path / ".ai" / "MEMORY.md").exists()
    assert (tmp_path / ".ai" / "HYPOTHESES.md").exists()
    assert (tmp_path / ".ai" / "STATUS.md").exists()
    assert (tmp_path / ".ai" / "DECISIONS.md").exists()
    assert (tmp_path / ".ai" / "WORKLOG.md").exists()
    assert (tmp_path / ".ai" / "KNOWLEDGE.md").exists()
    assert (tmp_path / ".ai" / "derived").is_dir()
    assert (tmp_path / ".ai" / "adr" / "index.md").exists()
    assert (tmp_path / ".ai" / "sessions" / "current.md").exists()
    assert (tmp_path / ".ai" / "history").is_dir()


def test_check_project_workflow(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "初始化项目")

    result = run_structured_workflow(tmp_path, "帮我看看项目怎么样")

    assert result.intent_name == "check_project"
    assert result.status == "success"
    assert "记忆层状态" in result.summary
    assert result.details["Project Charter"]
    assert "记忆漂移" in result.details
    assert result.next_steps


def test_continue_development_workflow(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "初始化项目")
    status_path = tmp_path / ".ai" / "STATUS.md"
    status_path.write_text("# Status\n\n当前阶段：测试阶段。\n\n下一步任务：补充测试。\n", encoding="utf-8")
    before = {
        name: (tmp_path / ".ai" / name).read_text(encoding="utf-8")
        for name in ("MEMORY.md", "HYPOTHESES.md", "ROADMAP.md", "DECISIONS.md")
    }

    result = run_structured_workflow(tmp_path, "继续开发项目")

    assert result.intent_name == "continue_development"
    assert result.status == "success"
    assert "测试阶段" in str(result.details["STATUS 摘要"])
    assert result.next_steps
    for name, content in before.items():
        assert (tmp_path / ".ai" / name).read_text(encoding="utf-8") == content


def test_session_candidate_updates_do_not_refresh_validation_snapshot(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "初始化项目")
    validation_path = tmp_path / ".ai" / "validation.json"
    before = validation_path.read_text(encoding="utf-8")

    memory = MemoryStore(tmp_path)
    memory.append_session_candidate("ADR Candidate", "今天先观察真实用户反馈。")

    assert validation_path.read_text(encoding="utf-8") == before


def test_continue_development_does_not_create_memory_layer(tmp_path: Path) -> None:
    result = run_structured_workflow(tmp_path, "继续开发项目")

    assert result.intent_name == "continue_development"
    assert result.status == "needs_input"
    assert "尚未安装项目记忆层" in result.title
    assert not (tmp_path / ".ai").exists()


def test_close_day_workflow(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "初始化项目")
    memory = MemoryStore(tmp_path)
    memory.append_session_candidate("ADR Candidate", "今天确认先做简历导入。")
    memory.append_session_candidate("Risk Candidate", "当前存在范围膨胀风险。")
    before_worklog = (tmp_path / ".ai" / "WORKLOG.md").read_text(encoding="utf-8")
    before_validation = (tmp_path / ".ai" / "validation.json").read_text(encoding="utf-8")

    result = run_structured_workflow(tmp_path, "今天结束工作")

    assert result.intent_name == "close_day"
    assert result.status == "success"
    assert "Session Archive" in result.title
    archive_files = list((tmp_path / ".ai" / "sessions" / "archive").rglob("*.md"))
    assert archive_files
    archive_text = archive_files[0].read_text(encoding="utf-8")
    assert "今天确认先做简历导入" in archive_text
    assert "当前存在范围膨胀风险" in archive_text
    current_text = (tmp_path / ".ai" / "sessions" / "current.md").read_text(encoding="utf-8")
    assert current_text.strip().startswith("# Current Session")
    assert "今天确认先做简历导入" not in current_text
    assert before_worklog == (tmp_path / ".ai" / "WORKLOG.md").read_text(encoding="utf-8")
    assert (tmp_path / ".ai" / "validation.json").read_text(encoding="utf-8") != before_validation
    assert (tmp_path / ".ai" / "derived" / "metrics.json").exists()


def test_record_decision_routes_uncertain_input_to_hypotheses(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "初始化项目")

    result = run_structured_workflow(tmp_path, "记录决策 也许先做简历导入")

    assert result.intent_name == "record_decision"
    assert result.status == "needs_input"
    assert "假设" in result.title
    assert "也许先做简历导入" in (tmp_path / ".ai" / "sessions" / "current.md").read_text(encoding="utf-8")
    assert "也许先做简历导入" not in (tmp_path / ".ai" / "DECISIONS.md").read_text(encoding="utf-8")


def test_record_decision_does_not_duplicate_into_memory(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "初始化项目")
    before = (tmp_path / ".ai" / "MEMORY.md").read_text(encoding="utf-8")

    result = run_structured_workflow(tmp_path, "记录决策 MVP 先做简历导入")

    assert result.intent_name == "record_decision"
    assert result.status == "success"
    assert "MVP 先做简历导入" not in (tmp_path / ".ai" / "DECISIONS.md").read_text(encoding="utf-8")
    assert "MVP 先做简历导入" in (tmp_path / ".ai" / "adr" / "index.md").read_text(encoding="utf-8")
    assert before == (tmp_path / ".ai" / "MEMORY.md").read_text(encoding="utf-8")


def test_init_project_splits_and_deduplicates_initial_decisions(tmp_path: Path) -> None:
    proposal = "\n".join(
        [
            "项目使命：AI 招聘系统",
            "目标用户：招聘团队",
            "商业目标：提高招聘筛选效率",
            "MVP 范围：简历导入",
            "技术栈：Python 3.11，本地规则驱动，pytest",
            "当前阶段：Sprint Proposal Driven Context",
            "初始 Roadmap：先做方案解析；再生成 .ai 记忆；最后补齐文档。",
            "初始 Decisions：先支持完整方案输入；保持本地运行。",
        ]
    )

    first = run_structured_workflow(tmp_path, proposal)
    second = run_structured_workflow(tmp_path, proposal)

    assert first.status == "success"
    assert second.status == "success"
    adr_files = sorted(path.name for path in (tmp_path / ".ai" / "adr").glob("*.md") if path.name != "index.md")
    assert adr_files == ["0001-decision.md", "0002-decision.md"]
    index_text = (tmp_path / ".ai" / "adr" / "index.md").read_text(encoding="utf-8")
    assert "暂无 ADR" not in index_text
    assert "先支持完整方案输入" in index_text
    assert "保持本地运行" in index_text


def test_natural_language_intent() -> None:
    assert classify_intent_name("这是一个新项目，请初始化") == "init_project"
    assert classify_intent_name("当前项目状态如何") == "check_project"
    assert classify_intent_name("继续开发") == "continue_development"
    assert classify_intent_name("今天收工") == "close_day"
    assert classify_intent_name("项目复盘") == "review_project"
    assert classify_intent_name("项目时间轴") == "timeline_project"
    assert classify_intent_name("项目偏航检查 新增商城模块") == "drift_check"
    assert classify_intent_name("记录决策 MVP 先做简历导入") == "record_decision"
    assert classify_intent_name("查看路线图") == "show_roadmap"


def _sample_proposal() -> str:
    return "\n".join(
        [
            "项目使命：AI 招聘系统",
            "目标用户：招聘团队",
            "商业目标：提高招聘筛选效率",
            "MVP 范围：简历导入",
            "技术栈：Python 3.11，本地规则驱动，pytest",
            "当前阶段：Sprint Proposal Driven Context",
            "初始 Roadmap：先做方案解析；再生成 .ai 记忆；最后补齐文档。",
            "初始 Decisions：先支持完整方案输入，缺失信息再追问；保持本地运行。",
        ]
    )
