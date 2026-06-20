import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from project_copilot.workflow import WorkflowEngine, run_text_workflow


class WorkflowEngineTest(unittest.TestCase):
    def test_registers_first_phase_workflows(self) -> None:
        engine = WorkflowEngine()

        self.assertIn("init_project", engine.registered_intents)
        self.assertIn("check_project", engine.registered_intents)
        self.assertIn("continue_development", engine.registered_intents)
        self.assertIn("close_day", engine.registered_intents)
        self.assertIn("sync_project_state", engine.registered_intents)
        self.assertIn("review_project", engine.registered_intents)
        self.assertIn("timeline_project", engine.registered_intents)
        self.assertIn("drift_check", engine.registered_intents)
        self.assertIn("record_decision", engine.registered_intents)
        self.assertIn("show_roadmap", engine.registered_intents)
        self.assertIn("refresh_validation_report", engine.registered_intents)
        self.assertIn("export_validation_snapshot", engine.registered_intents)

    def test_dispatches_from_natural_language(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            init_result = run_text_workflow(root, "初始化项目")
            check_result = run_text_workflow(root, "检查项目")

            self.assertIn("项目方案还需要补充", init_result)
            self.assertIn("Memory Health Summary", check_result)

    def test_unknown_intent_returns_suggestions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            result = run_text_workflow(root, "随便说点无法识别的话")

            self.assertIn("暂时没有识别这个意图", result)
            self.assertIn("检查项目", result)
            self.assertIn("项目复盘", result)

    def test_sync_project_state_only_refreshes_validation_derivatives(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".ai").mkdir()
            (root / ".ai" / "PROJECT_CHARTER.md").write_text("项目名称：测试项目\n", encoding="utf-8")
            (root / ".ai" / "MEMORY.md").write_text("# Memory\n\n## 长期事实\n\n- Existing fact.\n", encoding="utf-8")
            (root / ".ai" / "STATUS.md").write_text("# Status\n\n旧状态\n", encoding="utf-8")
            (root / ".ai" / "ROADMAP.md").write_text("- [x] Pytest baseline: 22 passed\n", encoding="utf-8")
            (root / "ROADMAP.md").write_text("- [x] Pytest baseline: 22 passed\n", encoding="utf-8")
            (root / "README.md").write_text("Current baseline:\n\n```text\n22 passed\n```\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("# Agents\n\n手写约定。\n", encoding="utf-8")
            before_memory = (root / ".ai" / "MEMORY.md").read_text(encoding="utf-8")
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## v0.3 Alpha\n\n### Added\n\n- Natural-language intent recognition.\n\n### Verified\n\n- `pytest -q`\n- Current baseline: 22 passed.\n",
                encoding="utf-8",
            )

            result = run_text_workflow(root, "同步项目状态")

            self.assertIn("已刷新派生记忆状态", result)
            self.assertIn("未运行测试", result)
            self.assertIn("22 passed", (root / "ROADMAP.md").read_text(encoding="utf-8"))
            self.assertIn("22 passed", (root / "README.md").read_text(encoding="utf-8"))
            self.assertIn("22 passed", (root / ".ai" / "ROADMAP.md").read_text(encoding="utf-8"))
            self.assertTrue((root / ".ai" / "validation.json").exists())
            self.assertEqual(before_memory, (root / ".ai" / "MEMORY.md").read_text(encoding="utf-8"))
            self.assertEqual("# Status\n\n旧状态\n", (root / ".ai" / "STATUS.md").read_text(encoding="utf-8"))
            changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
            self.assertIn("Current baseline: 22 passed.", changelog)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("手写约定。", agents)
            self.assertNotIn("project-copilot:managed:start", agents)

    def test_refresh_validation_report_ignores_stale_case_study_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project-copilot"
            root.mkdir()
            (root / "docs" / "case-studies").mkdir(parents=True)
            (root / "docs" / "case-studies" / "dashboard.md").write_text(
                "\n".join(
                    [
                        "项目名称：dashboard",
                        "开始使用日期：2026-06-17",
                        "当前状态：待接入",
                        "使用天数：0",
                        "工作日志数量：0",
                        "决策数量：0",
                        "知识沉淀数量：0",
                    ]
                ),
                encoding="utf-8",
            )
            sibling = Path(directory) / "dashboard" / ".ai"
            sibling.mkdir(parents=True)
            (sibling / "validation.json").write_text(
                "\n".join(
                    [
                        "{",
                        '  "project_name": "dashboard",',
                        '  "started_at": "2026-06-17",',
                        '  "status": "验证中",',
                        '  "usage_days": 3,',
                        '  "worklog_count": 5,',
                        '  "decision_count": 2,',
                        '  "knowledge_count": 1,',
                        '  "source": "project-copilot validation snapshot",',
                        '  "updated_at": "2026-06-18T09:00:00"',
                        "}",
                    ]
                ),
                encoding="utf-8",
            )

            result = run_text_workflow(root, "刷新验证报告")

            self.assertIn("已刷新验证报告", result)
            report = (root / "docs" / "validation-report.md").read_text(encoding="utf-8")
            self.assertIn("| dashboard | 2026-06-17 | 3 | 待记录 | 2 | 待记录 | 待记录 | 待记录 | 验证中 |", report)
            self.assertIn("README Drift", report)
            self.assertNotIn("待接入", report)
            self.assertIn("自动刷新", report)

    def test_refresh_validation_report_prefers_live_ai_over_stale_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project-copilot"
            root.mkdir()
            sibling = Path(directory) / "dashboard"
            ai_dir = sibling / ".ai"
            ai_dir.mkdir(parents=True)
            (ai_dir / "PROJECT_CONTEXT.md").write_text("项目名称：制造业利润管理系统 V1.0\n", encoding="utf-8")
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
                        "原因：避免手工整理。",
                        "",
                        "影响：后续按快照更新。",
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
                    ]
                ),
                encoding="utf-8",
            )
            (ai_dir / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
            (ai_dir / "validation.json").write_text(
                "\n".join(
                    [
                        "{",
                        '  "project_name": "制造业利润管理系统 V1.0",',
                        '  "started_at": "2026-06-17",',
                        '  "status": "可持续开发",',
                        '  "usage_days": 1,',
                        '  "worklog_count": 0,',
                        '  "decision_count": 0,',
                        '  "knowledge_count": 0,',
                        '  "source": "project-copilot validation snapshot",',
                        '  "updated_at": "2026-06-18T00:00:00"',
                        "}",
                    ]
                ),
                encoding="utf-8",
            )
            fixed_ts = datetime(2026, 6, 17, 12, 0).timestamp()
            for path in ai_dir.iterdir():
                os.utime(path, (fixed_ts, fixed_ts))

            result = run_text_workflow(root, "刷新验证报告")

            self.assertIn("已刷新验证报告", result)
            report = (root / "docs" / "validation-report.md").read_text(encoding="utf-8")
            self.assertIn("| 制造业利润管理系统 V1.0 | 2026-06-17 |", report)
            self.assertIn("| 缺失 | 0 | 0 | 0 | 存在 | 需要补齐记忆层 |", report)
            self.assertNotIn("| 制造业利润管理系统 V1.0 | 2026-06-17 | 3 | 待记录 | 0", report)
            self.assertIn("ADR Governance", report)

    def test_export_validation_snapshot_writes_ai_snapshot_and_refreshes_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "dashboard"
            root.mkdir()
            (root / ".ai").mkdir()
            (root / ".ai" / "PROJECT_CONTEXT.md").write_text("项目名称：dashboard\n", encoding="utf-8")
            (root / ".ai" / "STATUS.md").write_text("当前阶段：验证中\n", encoding="utf-8")
            (root / ".ai" / "WORKLOG.md").write_text(
                "# Worklog\n\n## 2026-06-16 09:00\n\n- 已更新项目状态。\n\n## 2026-06-17 09:00\n\n- 已更新项目状态。\n\n## 2026-06-18 09:00\n\n- 已更新项目状态。\n",
                encoding="utf-8",
            )
            (root / ".ai" / "DECISIONS.md").write_text(
                "# Decisions\n\n## 2026-06-16 09:00\n\n- 决策：先接入 dashboard。\n- 原因：验证自动汇总。\n- 影响：后续以快照为准。\n\n## 2026-06-18 09:00\n\n- 决策：保留自动刷新。\n- 原因：减少人工整理。\n- 影响：同步时自动收集。\n",
                encoding="utf-8",
            )
            (root / ".ai" / "KNOWLEDGE.md").write_text(
                "# Knowledge\n\n## 学到的最佳实践\n\n- 自动从 .ai 汇总验证数据。\n- 收工时同步快照。\n",
                encoding="utf-8",
            )
            (root / ".ai" / "ROADMAP.md").write_text("# Roadmap\n\n## In Progress\n\n- [ ] 自动收集验证汇总\n", encoding="utf-8")

            result = run_text_workflow(root, "导出验证快照")

            self.assertIn("已导出验证快照", result)
            self.assertIn("刷新验证报告", result)
            snapshot = root / ".ai" / "validation.json"
            self.assertTrue(snapshot.exists())
            payload = snapshot.read_text(encoding="utf-8")
            self.assertIn('"project_name": "dashboard"', payload)
            self.assertIn('"worklog_count": 3', payload)
            self.assertIn('"decision_count": 2', payload)
            self.assertIn('"knowledge_count": 2', payload)
            self.assertIn('"adr_count": 0', payload)
            self.assertIn('"readme_drift_status"', payload)
            self.assertIn('"legacy_migration_status"', payload)
            self.assertTrue((root / ".ai" / "derived" / "metrics.json").exists())
            report = root / "docs" / "validation-report.md"
            self.assertTrue(report.exists())
            self.assertIn("| dashboard |", report.read_text(encoding="utf-8"))
            self.assertIn("通常不需要手动刷新", run_text_workflow(root, "刷新验证报告"))
