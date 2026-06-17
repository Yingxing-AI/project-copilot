import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from project_copilot.cli.doctor import render_doctor
from project_copilot.cli.main import main, run_interactive
from project_copilot.secretary import status_label_from_health_score


class CliTest(unittest.TestCase):
    def test_command_line_text_still_runs_single_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            exit_code = main(["--root", directory, "检查项目"])

            self.assertEqual(exit_code, 0)

    def test_interactive_mode_shows_summary_runs_until_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            inputs = iter([_sample_proposal(), "退出"])
            outputs: list[str] = []

            exit_code = run_interactive(
                Path(directory),
                input_func=lambda _prompt: next(inputs),
                output_func=outputs.append,
            )

            rendered = "\n".join(outputs)
            self.assertEqual(exit_code, 0)
            self.assertIn("你好，我是你的项目秘书", rendered)
            self.assertIn("Codex 负责开发", rendered)
            self.assertIn("已生成 PROJECT_CONTEXT.md、STATUS.md、ROADMAP.md 和 DECISIONS.md", rendered)
            self.assertIn("项目状态：", rendered)
            self.assertIn("已退出", rendered)

    def test_interactive_mode_accepts_english_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            _write_project_context(tmp_path)
            outputs: list[str] = []

            exit_code = run_interactive(
                tmp_path,
                input_func=lambda _prompt: "quit",
                output_func=outputs.append,
            )

            self.assertEqual(exit_code, 0)
            self.assertIn("已退出。", outputs)

    def test_doctor_reports_environment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = render_doctor(Path(directory))

            self.assertIn("Project Copilot Doctor", result)
            self.assertIn("Python：", result)
            self.assertIn("Git：", result)
            self.assertIn("当前目录：", result)
            self.assertIn(".ai：", result)

    def test_doctor_command_runs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            exit_code = main(["--root", directory, "doctor"])

            self.assertEqual(exit_code, 0)

    def test_startup_secretary_intro(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            _write_project_context(tmp_path)
            outputs: list[str] = []

            exit_code = run_interactive(
                tmp_path,
                input_func=lambda _prompt: "退出",
                output_func=outputs.append,
            )

            rendered = "\n".join(outputs)
            self.assertEqual(exit_code, 0)
            self.assertIn("你好，我是你的项目秘书。", rendered)
            self.assertIn("* 记录项目历史", rendered)
            self.assertIn("* 保存重要决策", rendered)
            self.assertIn("* 提醒项目风险", rendered)
            self.assertIn("* 防止项目跑偏", rendered)
            self.assertIn("Codex 负责开发，", rendered)
            self.assertIn("我负责记住。", rendered)

    def test_status_label_from_health_score(self) -> None:
        self.assertEqual(status_label_from_health_score(100), "🟢 进展良好")
        self.assertEqual(status_label_from_health_score(85), "🟢 进展良好")
        self.assertEqual(status_label_from_health_score(84), "🟡 需要关注")
        self.assertEqual(status_label_from_health_score(60), "🟡 需要关注")
        self.assertEqual(status_label_from_health_score(59), "🔴 存在风险")
        self.assertEqual(status_label_from_health_score(0), "🔴 存在风险")

    def test_no_git_terms_in_startup_screen(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            _write_project_context(tmp_path)
            outputs: list[str] = []

            run_interactive(
                tmp_path,
                input_func=lambda _prompt: "退出",
                output_func=outputs.append,
            )

            rendered = "\n".join(outputs).lower()
            self.assertNotIn("git", rendered)
            self.assertNotIn("branch", rendered)
            self.assertNotIn("commit", rendered)
            self.assertNotIn("push", rendered)
            self.assertNotIn("tag", rendered)
            self.assertNotIn("release", rendered)
            self.assertNotIn("health score", rendered)
            self.assertNotIn("健康度：", rendered)

    def test_interactive_prompt_is_secretary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            _write_project_context(tmp_path)
            prompts: list[str] = []

            def input_func(prompt: str) -> str:
                prompts.append(prompt)
                return "退出"

            exit_code = run_interactive(tmp_path, input_func=input_func, output_func=lambda _text: None)

            self.assertEqual(exit_code, 0)
            self.assertEqual(prompts[-1], "项目秘书> ")

    def test_first_run_proposal_driven_onboarding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            answers = iter([_sample_proposal(), "退出"])
            prompts: list[str] = []

            def input_func(prompt: str) -> str:
                prompts.append(prompt)
                return next(answers)

            exit_code = run_interactive(tmp_path, input_func=input_func, output_func=lambda _text: None)

            context = (tmp_path / ".ai" / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")
            status = (tmp_path / ".ai" / "STATUS.md").read_text(encoding="utf-8")
            roadmap = (tmp_path / ".ai" / "ROADMAP.md").read_text(encoding="utf-8")
            decisions = (tmp_path / ".ai" / "DECISIONS.md").read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertIn("请直接输入完整项目方案", prompts[0])
            self.assertIn("项目使命：AI 招聘系统", context)
            self.assertIn("目标用户：招聘团队", context)
            self.assertIn("商业目标：提高招聘筛选效率", context)
            self.assertIn("MVP 范围：简历导入", context)
            self.assertIn("当前阶段：Sprint Proposal Driven Context", status)
            self.assertIn("先做方案解析", roadmap)
            self.assertIn("先支持完整方案输入", decisions)

    def test_first_run_prompts_for_missing_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            answers = iter([
                "\n".join(
                    [
                        "项目使命：AI 招聘系统",
                        "目标用户：招聘团队",
                        "MVP 范围：简历导入",
                        "技术栈：Python",
                        "当前阶段：方案确认中",
                        "初始 Roadmap：先做导入",
                        "初始 Decisions：先本地运行",
                    ]
                ),
                "商业目标：降低招聘成本。",
                "退出",
            ])
            prompts: list[str] = []
            outputs: list[str] = []

            def input_func(prompt: str) -> str:
                prompts.append(prompt)
                return next(answers)

            exit_code = run_interactive(tmp_path, input_func=input_func, output_func=outputs.append)

            self.assertEqual(exit_code, 0)
            self.assertTrue(any("还缺少这些关键信息" in output for output in outputs))
            context = (tmp_path / ".ai" / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")
            self.assertIn("商业目标：降低招聘成本", context)

    def test_noninteractive_startup_shows_codex_usage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            buffer = StringIO()

            with redirect_stdout(buffer):
                exit_code = main(["--root", directory])

            rendered = buffer.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("当前环境无法保持连续交互输入", rendered)
            self.assertIn("project-copilot 项目复盘", rendered)
            self.assertIn("project-copilot 结束工作", rendered)
            self.assertIn("project-copilot 项目时间轴", rendered)
            self.assertIn("project-copilot 项目偏航检查", rendered)


def _write_project_context(root: Path) -> None:
    ai_dir = root / ".ai"
    ai_dir.mkdir()
    (ai_dir / "PROJECT_CONTEXT.md").write_text(
        "# Project Context\n\n项目名称：测试项目\n\n项目是什么：测试。\n",
        encoding="utf-8",
    )


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
