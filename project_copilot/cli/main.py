from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path

from project_copilot import __version__
from project_copilot.cli.doctor import render_doctor
from project_copilot.memory import MemoryStore
from project_copilot.secretary import (
    render_noninteractive_help,
    render_recommended_commands,
    render_secretary_intro,
    render_status_card,
)
from project_copilot.workflow.init_project import build_project_context
from project_copilot.workflow import run_text_workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-copilot", description="Natural-language project workflow runner.")
    parser.add_argument("text", nargs="*", help="自然语言项目意图，例如：检查项目")
    parser.add_argument("--root", default=".", help="项目根目录，默认当前目录")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    text = " ".join(args.text).strip()
    if text.lower() == "doctor" or text == "检查秘书配置":
        print(render_doctor(root))
        return 0
    if not text:
        if not sys.stdin.isatty():
            print(render_secretary_intro())
            print()
            print(render_status_card(root))
            print()
            print(render_noninteractive_help())
            return 0
        return run_interactive(root)
    result = run_text_workflow(root, text)
    print(result)
    return 0


def run_interactive(
    root: Path,
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
) -> int:
    output_func(render_secretary_intro())
    if _needs_onboarding(root):
        _run_onboarding(root, input_func, output_func)
    output_func(render_status_card(root))
    output_func(render_recommended_commands())

    while True:
        try:
            text = input_func("项目秘书> ").strip()
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


def _needs_onboarding(root: Path) -> bool:
    return not (root / ".ai" / "PROJECT_CONTEXT.md").exists()


def _run_onboarding(
    root: Path,
    input_func: Callable[[str], str],
    output_func: Callable[[str], None],
) -> None:
    output_func("我会帮你记录项目历史、保存重要决策、提醒项目风险、防止项目跑偏。")
    output_func("先了解一下项目。")
    project_description = input_func("问题1：这个项目是做什么的？\n> ").strip()
    target_users = input_func("问题2：主要给谁使用？\n> ").strip()
    mvp = input_func("问题3：最小可交付版本（MVP）是什么？\n> ").strip()

    memory = MemoryStore(root)
    memory.ensure()
    (memory.ai_dir / "PROJECT_CONTEXT.md").write_text(
        build_project_context(root.name, project_description, target_users, mvp),
        encoding="utf-8",
    )
    memory.append_memory("完成首次问答式项目档案。")
    output_func("已生成 PROJECT_CONTEXT.md。")


if __name__ == "__main__":
    raise SystemExit(main())
