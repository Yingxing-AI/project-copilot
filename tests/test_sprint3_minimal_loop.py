from pathlib import Path

from project_copilot.intent import classify_intent_name
from project_copilot.workflow import run_structured_workflow


def test_init_project_workflow(tmp_path: Path) -> None:
    result = run_structured_workflow(tmp_path, "请初始化项目")

    assert result.intent_name == "init_project"
    assert result.status == "success"
    assert (tmp_path / ".ai" / "PROJECT_CONTEXT.md").exists()
    assert (tmp_path / ".ai" / "MEMORY.md").exists()
    assert (tmp_path / ".ai" / "STATUS.md").exists()
    assert (tmp_path / ".ai" / "DECISIONS.md").exists()
    assert (tmp_path / ".ai" / "WORKFLOW.md").exists()
    assert (tmp_path / ".ai" / "USER_PROFILE.md").exists()


def test_check_project_workflow(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "初始化项目")

    result = run_structured_workflow(tmp_path, "帮我看看项目怎么样")

    assert result.intent_name == "check_project"
    assert result.status == "success"
    assert "项目健康度评分" in result.summary
    assert result.details["当前开发阶段"]
    assert "当前风险" in result.details
    assert result.next_steps


def test_continue_development_workflow(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "初始化项目")
    status_path = tmp_path / ".ai" / "STATUS.md"
    status_path.write_text("# Status\n\n当前阶段：测试阶段。\n\n下一步任务：补充测试。\n", encoding="utf-8")

    result = run_structured_workflow(tmp_path, "继续开发项目")

    assert result.intent_name == "continue_development"
    assert result.status == "success"
    assert "测试阶段" in str(result.details["STATUS 摘要"])
    assert result.next_steps


def test_close_day_workflow(tmp_path: Path) -> None:
    run_structured_workflow(tmp_path, "初始化项目")

    result = run_structured_workflow(tmp_path, "今天结束工作")

    assert result.intent_name == "close_day"
    assert result.status == "success"
    assert (tmp_path / ".ai" / "STATUS.md").exists()
    assert (tmp_path / ".ai" / "WORKLOG.md").exists()
    assert "更新日期" in (tmp_path / ".ai" / "STATUS.md").read_text(encoding="utf-8")
    assert "已更新项目状态" in (tmp_path / ".ai" / "WORKLOG.md").read_text(encoding="utf-8")


def test_natural_language_intent() -> None:
    assert classify_intent_name("这是一个新项目，请初始化") == "init_project"
    assert classify_intent_name("当前项目状态如何") == "check_project"
    assert classify_intent_name("继续开发") == "continue_development"
    assert classify_intent_name("今天收工") == "close_day"
