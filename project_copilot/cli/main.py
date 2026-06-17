from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

from project_copilot import __version__
from project_copilot.cli.doctor import render_doctor
from project_copilot.memory import MemoryStore
from project_copilot.secretary import render_status_card
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
    if text.lower() == "doctor":
        print(render_doctor(root))
        return 0
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
    output_func("欢迎使用 Project Copilot。")
    output_func("我是你的项目秘书。")
    if _needs_onboarding(root):
        _run_onboarding(root, input_func, output_func)
    output_func(render_status_card(root))
    output_func("常用输入：项目状态、项目复盘、项目时间轴、项目偏航检查、记录决策、结束工作。")
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
