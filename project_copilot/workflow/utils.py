from __future__ import annotations


def format_next_steps(steps: list[str]) -> str:
    return "下一步建议：\n" + "\n".join(f"- {step}" for step in steps)


def as_bullets(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items]
