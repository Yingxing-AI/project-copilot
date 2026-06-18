import tempfile
import unittest
import subprocess
from pathlib import Path

from project_copilot.planner import run_workflow


class WorkflowTest(unittest.TestCase):
    def test_init_project_creates_memory_and_project_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            proposal = "这是一个 AI 招聘系统，请初始化项目"
            result = run_workflow(tmp_path, proposal)

            self.assertIn("项目方案还需要补充", result)
            self.assertTrue((tmp_path / "README.md").exists())
            self.assertTrue((tmp_path / "LICENSE").exists())
            self.assertTrue((tmp_path / "AGENTS.md").exists())
            self.assertTrue((tmp_path / "docs").is_dir())
            self.assertTrue((tmp_path / ".ai" / "PROJECT_CONTEXT.md").exists())
            self.assertTrue((tmp_path / ".ai" / "MEMORY.md").exists())
            self.assertTrue((tmp_path / ".ai" / "HYPOTHESES.md").exists())
            self.assertTrue((tmp_path / ".ai" / "KNOWLEDGE.md").exists())
            self.assertTrue((tmp_path / ".ai" / "metrics.md").exists())
            self.assertTrue((tmp_path / ".ai" / "history").is_dir())
            self.assertIn("完成首次方案驱动项目档案初始化。", (tmp_path / ".ai" / "MEMORY.md").read_text(encoding="utf-8"))
            self.assertNotIn(proposal, (tmp_path / ".ai" / "MEMORY.md").read_text(encoding="utf-8"))

    def test_run_workflow_uses_git_toplevel_as_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            subprocess.run(["git", "init"], cwd=tmp_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            nested = tmp_path / "apps" / "dashboard"
            nested.mkdir(parents=True)

            run_workflow(nested, "初始化项目")

            self.assertTrue((tmp_path / ".ai" / "PROJECT_CONTEXT.md").exists())
            self.assertFalse((nested / ".ai").exists())

    def test_check_project_reports_health_score(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            run_workflow(tmp_path, "初始化项目")
            result = run_workflow(tmp_path, "检查项目")

            self.assertIn("项目健康度", result)
            self.assertIn("当前阶段", result)
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
            self.assertIn("完成已有项目接管。", (tmp_path / ".ai" / "MEMORY.md").read_text(encoding="utf-8"))
            self.assertNotIn("接管这个已有项目", (tmp_path / ".ai" / "MEMORY.md").read_text(encoding="utf-8"))

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

    def test_secretary_review_timeline_decision_and_drift_check(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            run_workflow(tmp_path, "这是一个 AI 招聘系统，请初始化项目")

            decision = run_workflow(tmp_path, "记录决策 MVP 先做简历导入")
            before_memory = (tmp_path / ".ai" / "MEMORY.md").read_text(encoding="utf-8")
            review = run_workflow(tmp_path, "项目复盘")
            timeline = run_workflow(tmp_path, "项目时间轴")
            drift = run_workflow(tmp_path, "项目偏航检查 新增商城模块")
            roadmap = run_workflow(tmp_path, "查看路线图")

            self.assertIn("已记录决策", decision)
            self.assertIn("MVP 先做简历导入", (tmp_path / ".ai" / "DECISIONS.md").read_text(encoding="utf-8"))
            self.assertIn("项目健康度", review)
            self.assertTrue((tmp_path / ".ai" / "history" / "2026-06.md").exists())
            self.assertIn("# History 2026-06", (tmp_path / ".ai" / "history" / "2026-06.md").read_text(encoding="utf-8"))
            self.assertIn("项目健康度：", (tmp_path / ".ai" / "history" / "2026-06.md").read_text(encoding="utf-8"))
            self.assertIn("下一步：", (tmp_path / ".ai" / "history" / "2026-06.md").read_text(encoding="utf-8"))
            self.assertEqual(before_memory, (tmp_path / ".ai" / "MEMORY.md").read_text(encoding="utf-8"))
            self.assertIn("项目时间轴", timeline)
            self.assertIn("最近里程碑：", timeline)
            self.assertIn("近期工作：", timeline)
            self.assertIn("关键决策：", timeline)
            self.assertIn("可能不在 MVP 范围内", drift)
            self.assertIn("项目路线图", roadmap)

    def test_review_project_limits_key_decisions_to_recent_three(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            run_workflow(tmp_path, "初始化项目")
            for item in (
                "记录决策 MVP 先做简历导入",
                "记录决策 第二条决策",
                "记录决策 第三条决策",
                "记录决策 第四条决策",
            ):
                run_workflow(tmp_path, item)

            review = run_workflow(tmp_path, "项目复盘")

            self.assertIn("第三条决策", review)
            self.assertIn("第四条决策", review)
            self.assertIn("第二条决策", review)
            self.assertNotIn("MVP 先做简历导入", review)

    def test_record_decision_uncertain_input_routes_to_hypotheses(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            run_workflow(tmp_path, "初始化项目")

            result = run_workflow(tmp_path, "记录决策 可能先做简历导入")

            self.assertIn("假设", result)
            self.assertIn("可能先做简历导入", (tmp_path / ".ai" / "HYPOTHESES.md").read_text(encoding="utf-8"))
            self.assertNotIn("可能先做简历导入", (tmp_path / ".ai" / "DECISIONS.md").read_text(encoding="utf-8"))
