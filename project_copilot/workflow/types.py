from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class WorkflowContext:
    root: Path
    text: str
    intent_name: str


@dataclass(frozen=True)
class WorkflowResult:
    intent_name: str
    status: str
    title: str
    summary: str
    details: dict[str, object] = field(default_factory=dict)
    next_steps: list[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [self.title, self.summary]
        for key, value in self.details.items():
            if value in (None, "", [], {}):
                continue
            if isinstance(value, list):
                lines.append(f"{key}：" + ", ".join(str(item) for item in value))
            else:
                lines.append(f"{key}：{value}")
        if self.next_steps:
            lines.append("下一步建议：")
            lines.extend(f"- {step}" for step in self.next_steps)
        return "\n".join(lines)
