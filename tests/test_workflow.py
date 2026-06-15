import tempfile
import unittest
from pathlib import Path

from project_copilot.planner import run_workflow


class WorkflowTest(unittest.TestCase):
    def test_init_project_creates_memory_and_project_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            result = run_workflow(tmp_path, "这是一个 AI 招聘系统，请初始化项目")

            self.assertIn("已完成项目初始化", result)
            self.assertTrue((tmp_path / "README.md").exists())
            self.assertTrue((tmp_path / "LICENSE").exists())
            self.assertTrue((tmp_path / "AGENTS.md").exists())
            self.assertTrue((tmp_path / "docs").is_dir())
            self.assertTrue((tmp_path / ".ai" / "PROJECT_CONTEXT.md").exists())
            self.assertTrue((tmp_path / ".ai" / "MEMORY.md").exists())

    def test_check_project_reports_health_score(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            run_workflow(tmp_path, "初始化项目")
            result = run_workflow(tmp_path, "检查项目")

            self.assertIn("项目健康度评分", result)
            self.assertIn("当前开发阶段", result)
            self.assertIn("下一步建议", result)

    def test_adopt_existing_project_does_not_overwrite_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            readme = tmp_path / "README.md"
            package_json = tmp_path / "package.json"
            readme.write_text("# Existing App\n", encoding="utf-8")
            package_json.write_text('{"scripts": {"test": "node test.js"}}\n', encoding="utf-8")

            result = run_workflow(tmp_path, "接管这个已有项目")

            self.assertIn("已接管已有项目", result)
            self.assertIn("Node.js", result)
            self.assertEqual(readme.read_text(encoding="utf-8"), "# Existing App\n")
            self.assertTrue((tmp_path / ".ai" / "PROJECT_CONTEXT.md").exists())
            self.assertIn(
                "package.json",
                (tmp_path / ".ai" / "PROJECT_CONTEXT.md").read_text(encoding="utf-8"),
            )

    def test_oss_readiness_reports_missing_items(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            run_workflow(tmp_path, "初始化项目")
            result = run_workflow(tmp_path, "检查 OSS 准备度")

            self.assertIn("OSS Readiness Score", result)
            self.assertIn("缺失", result)

    def test_end_work_updates_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            run_workflow(tmp_path, "初始化项目")
            result = run_workflow(tmp_path, "今天结束工作")

            self.assertIn("已更新项目状态", result)
            self.assertIn("更新日期", (tmp_path / ".ai" / "STATUS.md").read_text(encoding="utf-8"))
