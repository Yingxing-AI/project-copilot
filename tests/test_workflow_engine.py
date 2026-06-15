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

    def test_dispatches_from_natural_language(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            init_result = run_text_workflow(root, "初始化项目")
            check_result = run_text_workflow(root, "检查项目")

            self.assertIn("已完成项目初始化", init_result)
            self.assertIn("项目健康度评分", check_result)

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

    def test_github_sync_reports_visibility_and_missing_prerequisites(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            result = run_text_workflow(root, "私有同步到GitHub")

            self.assertIn("GitHub 同步计划", result)
            self.assertIn("仓库可见性：private", result)
            self.assertIn("仓库名称：", result)
            self.assertIn("GitHub CLI", result)
            self.assertIn("GitHub 登录", result)
