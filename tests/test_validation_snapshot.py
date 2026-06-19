from pathlib import Path

from project_copilot.memory.health import inspect_memory_health
from project_copilot.validation.snapshot import collect_validation_snapshot


def test_collect_validation_snapshot_accepts_legacy_ai_formats(tmp_path: Path) -> None:
    ai_dir = tmp_path / ".ai"
    ai_dir.mkdir()
    (ai_dir / "PROJECT_CONTEXT.md").write_text("项目名称：legacy-project\n", encoding="utf-8")
    (ai_dir / "STATUS.md").write_text("当前阶段：可持续开发\n", encoding="utf-8")
    (ai_dir / "WORKLOG.md").write_text(
        "\n".join(
            [
                "# Worklog",
                "",
                "2026-06-18",
                "- 完成内容：第一条。",
                "- 遇到问题：无。",
                "- 明日计划：继续。",
                "",
                "2026-06-18",
                "- 完成内容：第二条。",
                "- 遇到问题：无。",
                "- 明日计划：继续。",
            ]
        ),
        encoding="utf-8",
    )
    (ai_dir / "DECISIONS.md").write_text(
        "\n".join(
            [
                "# Decisions",
                "",
                "日期：2026-06-17",
                "",
                "决策：保留自动汇总。",
                "",
                "原因：避免手工汇总。",
                "",
                "影响：后续按快照更新。",
                "",
                "日期：2026-06-18",
                "",
                "决策：兼容旧格式。",
                "",
                "原因：不迁移历史文件。",
                "",
                "影响：统计口径可持续。",
            ]
        ),
        encoding="utf-8",
    )
    (ai_dir / "KNOWLEDGE.md").write_text(
        "\n".join(
            [
                "# Knowledge",
                "",
                "## 学到的最佳实践",
                "",
                "- 自动统计应兼容旧格式。",
                "- 迁移应作为独立动作。",
                "",
                "## 产品认知",
                "",
                "- 真实项目不应被统计口径误伤。",
            ]
        ),
        encoding="utf-8",
    )
    (ai_dir / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    (ai_dir / "sessions" / "current.md").parent.mkdir(parents=True, exist_ok=True)
    (ai_dir / "sessions" / "current.md").write_text(
        "# Current Session\n\n## 候选事件\n\n- 2026-06-19 09:00 [Milestone Candidate] 完成 Session Archive 设计。\n",
        encoding="utf-8",
    )
    (ai_dir / "sessions" / "archive" / "2026-06").mkdir(parents=True, exist_ok=True)
    (ai_dir / "sessions" / "archive" / "2026-06" / "2026-06-18.md").write_text(
        "# Session Archive\n\n## 09:00\n\n- 完成 Session Archive 设计。\n",
        encoding="utf-8",
    )

    snapshot = collect_validation_snapshot(tmp_path)
    health = inspect_memory_health(tmp_path)

    assert snapshot is not None
    assert snapshot.project_name == "legacy-project"
    assert snapshot.worklog_count == 2
    assert snapshot.decision_count == 2
    assert snapshot.knowledge_count == 3
    assert snapshot.session_archive_count == 1
    assert snapshot.active_candidate_count == 1
    assert health.session_archive_count == 1
    assert health.active_candidate_count == 1
