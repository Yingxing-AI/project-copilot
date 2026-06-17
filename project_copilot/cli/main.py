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
from project_copilot.workflow.init_project import _write_initial_memory
from project_copilot.workflow.project_proposal import parse_project_proposal, project_proposal_prompt
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
    output_func("我会先分析你给出的完整项目方案，再只追问缺失项。")
    output_func("请尽量一次性贴出项目使命、目标用户、商业目标、MVP 范围、技术栈、当前阶段、初始 Roadmap 和初始 Decisions。")
    proposal_text = input_func("请直接输入完整项目方案：\n> ").strip()
    proposal = parse_project_proposal(proposal_text, root.name)
    while proposal.missing_fields:
        output_func(project_proposal_prompt(proposal.missing_fields))
        extra = input_func("> ").strip()
        if not extra:
            break
        proposal_text = "\n".join(part for part in (proposal_text, extra) if part.strip())
        proposal = parse_project_proposal(proposal_text, root.name)

    memory = MemoryStore(root)
    memory.ensure()
    _write_initial_memory(memory, proposal)
    memory.append_memory("完成首次方案驱动项目档案。")
    output_func("已生成 PROJECT_CONTEXT.md、STATUS.md、ROADMAP.md 和 DECISIONS.md。")
    if proposal.missing_fields:
        output_func(f"仍有待补充信息：{'、'.join(proposal.missing_fields)}")


if __name__ == "__main__":
    raise SystemExit(main())
