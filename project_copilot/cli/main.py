from __future__ import annotations

import argparse
from pathlib import Path

from project_copilot.workflow import run_text_workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-copilot", description="Natural-language project workflow runner.")
    parser.add_argument("text", nargs="*", help="自然语言项目意图，例如：检查项目")
    parser.add_argument("--root", default=".", help="项目根目录，默认当前目录")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    text = " ".join(args.text).strip()
    if not text:
        text = input("请输入项目意图：").strip()
    result = run_text_workflow(Path(args.root).resolve(), text)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
