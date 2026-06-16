from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

from project_copilot.analyzer import analyze_project
from project_copilot.workflow import run_text_workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-copilot", description="Natural-language project workflow runner.")
    parser.add_argument("text", nargs="*", help="自然语言项目意图，例如：检查项目")
    parser.add_argument("--root", default=".", help="项目根目录，默认当前目录")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    text = " ".join(args.text).strip()
    if not text:
        return run_interactive(root)
    result = run_text_workflow(root, text)
    print(result)
    return 0


def run_interactive(
    root: Path,
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
) -> int:
    output_func("Project Copilot 交互模式")
    output_func(_render_startup_summary(root))
    output_func(_render_first_use_guide(root))
    output_func("输入 exit / quit / 退出 结束。")

    while True:
        try:
            text = input_func("project-copilot> ").strip()
        except EOFError:
            output_func("已结束。")
            return 0

        if not text:
            continue
        if _is_exit_command(text):
            output_func("已退出。")
            return 0

        output_func(run_text_workflow(root, text))


def _is_exit_command(text: str) -> bool:
    return text.strip().lower() in {"exit", "quit", "退出"}


def _render_startup_summary(root: Path) -> str:
    analysis = analyze_project(root)
    git_summary = "Git：未初始化"
    if analysis.git.initialized:
        branch = analysis.git.branch or "未知分支"
        git_summary = f"Git：{branch}"
    return "\n".join(
        [
            "项目状态摘要：",
            f"- 当前阶段：{analysis.stage}",
            f"- 健康度：{analysis.health_score}/100",
            f"- {git_summary}",
        ]
    )


def _render_first_use_guide(root: Path) -> str:
    if not (root / ".ai" / "PROJECT_CONTEXT.md").exists():
        return "首次使用建议：输入“初始化项目”创建项目记忆，或输入“接管已有项目”纳入现有项目。"
    return "常用输入：检查项目、继续开发项目、今天结束工作、检查 OSS 准备度。"


if __name__ == "__main__":
    raise SystemExit(main())
