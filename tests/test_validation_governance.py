from datetime import datetime, timedelta
from pathlib import Path

from project_copilot.validation.governance import (
    inspect_adr_governance,
    inspect_legacy_migration,
    inspect_readme_drift,
    inspect_session_quality,
    load_validation_project_roots,
)
from project_copilot.validation.snapshot import collect_validation_snapshot, export_validation_snapshot


def test_validation_governance_reports_new_p2_signals(tmp_path: Path) -> None:
    root = tmp_path / "project-copilot"
    root.mkdir()
    ai_dir = root / ".ai"
    (ai_dir / "adr").mkdir(parents=True)
    (ai_dir / "sessions" / "archive" / "2026-06").mkdir(parents=True, exist_ok=True)
    (ai_dir / "derived").mkdir(parents=True, exist_ok=True)

    (root / "README.md").write_text(
        "\n".join(
            [
                "# Project Copilot",
                "",
                "## Available Today",
                "",
                "- Project status card",
                "- Validation snapshots derived from real `.ai`",
            ]
        ),
        encoding="utf-8",
    )
    (ai_dir / "PROJECT_CHARTER.md").write_text("项目名称：Project Copilot\n", encoding="utf-8")
    (ai_dir / "PROJECT_CONTEXT.md").write_text("项目名称：Project Copilot\n", encoding="utf-8")
    (ai_dir / "STATUS.md").write_text("当前阶段：可持续开发\n", encoding="utf-8")
    (ai_dir / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    (ai_dir / "WORKLOG.md").write_text("# Worklog\n\n## 2026-06-19\n\n- 已更新项目状态。\n", encoding="utf-8")
    (ai_dir / "HYPOTHESES.md").write_text("# Hypotheses\n\n- 仍需观察第二个样本。\n", encoding="utf-8")
    (ai_dir / "DECISIONS.md").write_text("# Decisions\n\n- 决策：兼容旧索引。\n", encoding="utf-8")
    (ai_dir / "metrics.md").write_text("# Metrics\n\n- 这是旧快照。\n", encoding="utf-8")
    (ai_dir / "adr" / "0001-test.md").write_text(
        "# ADR 0001: Test\n\n日期：2026-06-19\n\n状态：Superseded\n",
        encoding="utf-8",
    )
    (ai_dir / "sessions" / "archive" / "2026-06" / "2026-06-19.md").write_text(
        "# Session Archive\n\n日期：2026-06-19\n\n## 今日关键进展\n- 暂无。\n",
        encoding="utf-8",
    )
    (ai_dir / "derived" / "metrics.json").write_text("{}", encoding="utf-8")

    snapshot = collect_validation_snapshot(root)

    assert snapshot is not None
    assert snapshot.readme_drift_status == "存在漂移"
    assert snapshot.adr_governance_status == "需要治理"
    assert snapshot.session_quality_status == "需要治理"
    assert snapshot.legacy_migration_status == "迁移未完成"
    assert snapshot.legacy_migration_classifications == {
        "PROJECT_CONTEXT.md": "Compatibility",
        "DECISIONS.md": "Compatibility",
        "WORKLOG.md": "Legacy",
        "HYPOTHESES.md": "Legacy",
        "metrics.md": "Compatibility",
    }

    export_validation_snapshot(root, snapshot)
    metrics = (ai_dir / "derived" / "metrics.json").read_text(encoding="utf-8")
    assert '"readme_drift_status": "存在漂移"' in metrics
    assert '"adr_governance_issue_count": 1' in metrics
    assert '"session_quality_issue_count": 2' in metrics
    assert '"legacy_migration_status": "迁移未完成"' in metrics


def test_readme_drift_and_session_quality_rules_are_rule_based(tmp_path: Path) -> None:
    root = tmp_path
    ai_dir = root / ".ai"
    (ai_dir / "adr").mkdir(parents=True)
    (ai_dir / "sessions" / "archive" / "2026-06").mkdir(parents=True)
    (root / "README.md").write_text("# Project Copilot\n\n## Available Today\n\n- Project status card\n", encoding="utf-8")
    (ai_dir / "PROJECT_CHARTER.md").write_text("项目名称：Project Copilot\n", encoding="utf-8")
    (ai_dir / "STATUS.md").write_text("当前阶段：可持续开发\n", encoding="utf-8")
    (ai_dir / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    (ai_dir / "adr" / "0001-test.md").write_text(
        "# ADR 0001: Test\n\n日期：2026-06-19\n\n状态：Accepted\n",
        encoding="utf-8",
    )
    (ai_dir / "sessions" / "archive" / "2026-06" / "2026-06-19.md").write_text(
        "\n".join(
            [
                "# Session Archive",
                "",
                "日期：2026-06-19",
                "",
                "## 今日关键进展",
                "- 已更新项目状态。",
                "- 运行测试。",
                "- 同步文档。",
                "",
                "## ADR 复制",
                "背景：x",
                "决策：y",
                "原因：z",
            ]
        ),
        encoding="utf-8",
    )

    readme_report = inspect_readme_drift(root)
    session_report = inspect_session_quality(root)

    assert any("Project status card" in issue for issue in readme_report.issues)
    assert any("README Drift Check" in issue for issue in readme_report.issues)
    assert any("疑似重复 ADR 正文" in issue for issue in session_report.issues)
    assert any("噪音占比过高" in issue for issue in session_report.issues)


def test_readme_drift_ignores_fresh_validation_artifacts(tmp_path: Path) -> None:
    root = tmp_path
    ai_dir = root / ".ai"
    (ai_dir / "adr").mkdir(parents=True)
    (ai_dir / "sessions" / "archive" / "2026-06").mkdir(parents=True)
    (ai_dir / "derived").mkdir(parents=True)

    readme = root / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Project Copilot",
                "",
                "## Available Today",
                "",
                "- Memory Health",
                "- README Drift Check",
                "- ADR Governance",
                "- Session Quality",
                "- Legacy Migration Report",
                "- Multi-Project Validation",
            ]
        ),
        encoding="utf-8",
    )
    (ai_dir / "PROJECT_CHARTER.md").write_text("项目名称：Project Copilot\n", encoding="utf-8")
    (ai_dir / "STATUS.md").write_text("当前阶段：可持续开发\n", encoding="utf-8")
    (ai_dir / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    (ai_dir / "adr" / "0001-test.md").write_text(
        "# ADR 0001: Test\n\n日期：2026-06-19\n\n状态：Accepted\n",
        encoding="utf-8",
    )
    (ai_dir / "sessions" / "archive" / "2026-06" / "2026-06-19.md").write_text(
        "# Session Archive\n\n日期：2026-06-19\n\n## 今日关键进展\n- 完成对齐。\n",
        encoding="utf-8",
    )
    (ai_dir / "validation.json").write_text("{}", encoding="utf-8")
    (ai_dir / "derived" / "metrics.json").write_text("{}", encoding="utf-8")

    base = datetime(2026, 6, 22, 10, 0, 0).timestamp()
    newer = (datetime(2026, 6, 22, 10, 0, 0) + timedelta(hours=1)).timestamp()
    for path in (
        readme,
        ai_dir / "PROJECT_CHARTER.md",
        ai_dir / "STATUS.md",
        ai_dir / "ROADMAP.md",
        ai_dir / "adr" / "0001-test.md",
        ai_dir / "sessions" / "archive" / "2026-06" / "2026-06-19.md",
    ):
        path.touch()
        path.chmod(path.stat().st_mode)
        import os
        os.utime(path, (base, base))
    for path in (ai_dir / "validation.json", ai_dir / "derived" / "metrics.json"):
        import os
        os.utime(path, (newer, newer))

    report = inspect_readme_drift(root)

    assert report.status == "已对齐"
    assert not any("核心记忆约" in issue for issue in report.issues)


def test_adr_governance_detects_missing_status_and_broken_superseded_chain(tmp_path: Path) -> None:
    adr_dir = tmp_path / ".ai" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "0001-a.md").write_text("# ADR 0001: A\n\n日期：2026-06-19\n\n状态：Superseded\n", encoding="utf-8")
    (adr_dir / "0002-b.md").write_text(
        "# ADR 0002: B\n\n日期：2026-06-19\n\nSuperseded By：ADR-0003\n",
        encoding="utf-8",
    )

    report = inspect_adr_governance(tmp_path)

    assert report.status == "需要治理"
    assert any("缺少 `Superseded By:`" in issue for issue in report.issues)
    assert any("缺少 `状态：` 字段" in issue for issue in report.issues)
    assert any("对应 ADR 不存在" in issue for issue in report.issues)


def test_validation_sources_yaml_controls_multi_project_scan(tmp_path: Path) -> None:
    root = tmp_path / "project-copilot"
    root.mkdir()
    (tmp_path / "ai-recruitment").mkdir()
    (tmp_path / "dashboard").mkdir()
    (tmp_path / "ignored-project").mkdir()
    config_dir = root / "validation"
    config_dir.mkdir()
    (config_dir / "sources.yaml").write_text(
        "projects:\n  - project-copilot\n  - ai-recruitment\n  - dashboard\n",
        encoding="utf-8",
    )

    roots = load_validation_project_roots(root)

    assert roots == [root.resolve(), (tmp_path / "ai-recruitment").resolve(), (tmp_path / "dashboard").resolve()]


def test_legacy_migration_report_tracks_active_vs_compatibility(tmp_path: Path) -> None:
    ai_dir = tmp_path / ".ai"
    ai_dir.mkdir()
    (ai_dir / "WORKLOG.md").write_text("# Worklog\n\n暂无工作记录。\n", encoding="utf-8")
    (ai_dir / "HYPOTHESES.md").write_text("# Hypotheses\n\n暂无。\n", encoding="utf-8")

    report = inspect_legacy_migration(tmp_path)

    assert report.classifications["PROJECT_CONTEXT.md"] == "Active"
    assert report.classifications["DECISIONS.md"] == "Active"
    assert report.classifications["WORKLOG.md"] == "Compatibility"
    assert report.classifications["HYPOTHESES.md"] == "Compatibility"
    assert report.classifications["metrics.md"] == "Safe To Remove"
