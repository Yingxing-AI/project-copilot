import tempfile
import unittest
from pathlib import Path

from project_copilot.cli.doctor import render_doctor
from project_copilot.cli.main import main, run_interactive


class CliTest(unittest.TestCase):
    def test_command_line_text_still_runs_single_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            exit_code = main(["--root", directory, "检查项目"])

            self.assertEqual(exit_code, 0)

    def test_interactive_mode_shows_summary_runs_until_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            inputs = iter(["检查项目", "随便说点无法识别的话", "退出"])
            outputs: list[str] = []

            exit_code = run_interactive(
                Path(directory),
                input_func=lambda _prompt: next(inputs),
                output_func=outputs.append,
            )

            rendered = "\n".join(outputs)
            self.assertEqual(exit_code, 0)
            self.assertIn("Project Copilot 交互模式", rendered)
            self.assertIn("项目状态摘要", rendered)
            self.assertIn("首次使用建议", rendered)
            self.assertIn("项目状态检查完成", rendered)
            self.assertIn("暂时没有识别这个意图", rendered)
            self.assertIn("已退出", rendered)

    def test_interactive_mode_accepts_english_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outputs: list[str] = []

            exit_code = run_interactive(
                Path(directory),
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
