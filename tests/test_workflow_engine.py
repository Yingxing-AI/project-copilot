import tempfile
import unittest
from pathlib import Path

from project_copilot.workflow import WorkflowEngine, run_text_workflow


class WorkflowEngineTest(unittest.TestCase):
    def test_registers_first_phase_workflows(self) -> None:
        engine = WorkflowEngine()

        self.assertIn("init_project", engine.registered_intents)
        self.assertIn("check_project", engine.registered_intents)
        self.assertIn("continue_development", engine.registered_intents)
        self.assertIn("close_day", engine.registered_intents)
        self.assertIn("oss_check", engine.registered_intents)
        self.assertIn("prepare_oss", engine.registered_intents)
        self.assertIn("github_sync", engine.registered_intents)
        self.assertIn("sync_project_state", engine.registered_intents)
        self.assertIn("release_project", engine.registered_intents)
        self.assertIn("review_project", engine.registered_intents)
        self.assertIn("timeline_project", engine.registered_intents)
        self.assertIn("drift_check", engine.registered_intents)
        self.assertIn("record_decision", engine.registered_intents)
        self.assertIn("show_roadmap", engine.registered_intents)

    def test_dispatches_from_natural_language(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            init_result = run_text_workflow(root, "初始化项目")
            check_result = run_text_workflow(root, "检查项目")

            self.assertIn("已完成项目档案初始化", init_result)
            self.assertIn("项目健康度", check_result)

    def test_prepare_oss_creates_open_source_files_without_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "README.md"
            readme.write_text("# Existing README\n", encoding="utf-8")

            result = run_text_workflow(root, "准备开源")

            self.assertIn("已完成开源准备文件检查", result)
            self.assertEqual(readme.read_text(encoding="utf-8"), "# Existing README\n")
            self.assertTrue((root / "LICENSE").exists())
            self.assertTrue((root / "CONTRIBUTING.md").exists())
            self.assertTrue((root / "CODE_OF_CONDUCT.md").exists())
            self.assertTrue((root / "SECURITY.md").exists())
            self.assertTrue((root / "CHANGELOG.md").exists())
            self.assertTrue((root / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml").exists())
            self.assertTrue((root / ".github" / "pull_request_template.md").exists())
            contributing = (root / "CONTRIBUTING.md").read_text(encoding="utf-8")
            self.assertIn("pytest -q", contributing)
            self.assertNotIn("python3 -m unittest discover", contributing)

    def test_github_sync_reports_visibility_and_missing_prerequisites(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            result = run_text_workflow(root, "备份到云端")

            self.assertIn("云端备份计划", result)
            self.assertIn("备份空间：公开备份", result)
            self.assertIn("项目名称：", result)
            self.assertIn("云端工具", result)
            self.assertIn("云端登录", result)

    def test_unknown_intent_returns_suggestions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            result = run_text_workflow(root, "随便说点无法识别的话")

            self.assertIn("暂时没有识别这个意图", result)
            self.assertIn("检查项目", result)
            self.assertIn("项目复盘", result)

    def test_sync_project_state_updates_status_roadmap_and_changelog(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".ai").mkdir()
            (root / ".ai" / "STATUS.md").write_text("# Status\n\n旧状态\n", encoding="utf-8")
            (root / ".ai" / "ROADMAP.md").write_text("- [x] Pytest baseline: 22 passed\n", encoding="utf-8")
            (root / "ROADMAP.md").write_text("- [x] Pytest baseline: 22 passed\n", encoding="utf-8")
            (root / "README.md").write_text("Current baseline:\n\n```text\n22 passed\n```\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("# Agents\n\n手写约定。\n", encoding="utf-8")
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## v0.3 Alpha\n\n### Added\n\n- Natural-language intent recognition.\n\n### Verified\n\n- `pytest -q`\n- Current baseline: 22 passed.\n",
                encoding="utf-8",
            )

            result = run_text_workflow(root, "同步项目状态")

            self.assertIn("已同步项目状态", result)
            self.assertNotIn("22 passed", (root / "ROADMAP.md").read_text(encoding="utf-8"))
            self.assertNotIn("22 passed", (root / "README.md").read_text(encoding="utf-8"))
            self.assertNotIn("22 passed", (root / ".ai" / "ROADMAP.md").read_text(encoding="utf-8"))
            self.assertIn("测试基线", (root / ".ai" / "STATUS.md").read_text(encoding="utf-8"))
            status = (root / ".ai" / "STATUS.md").read_text(encoding="utf-8")
            self.assertIn("Codex Native 主流程", status)
            self.assertIn("记忆层安装器", status)
            self.assertNotIn("像 Codex 项目的项目秘书", status)
            changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
            self.assertNotIn("Current baseline: 22 passed.", changelog)
            self.assertIn("`project-copilot doctor`", changelog)
            self.assertIn("Managed `AGENTS.md` synchronization block.", changelog)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("手写约定。", agents)
            self.assertIn("project-copilot:managed:start", agents)
            self.assertIn("project-copilot doctor", agents)

    def test_release_project_requires_tag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_text_workflow(Path(directory), "一键发布")

            self.assertIn("发布被阻止", result)
            self.assertIn("请提供明确版本标记", result)
