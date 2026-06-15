from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


MEMORY_FILES = {
    "PROJECT_CONTEXT.md": "# Project Context\n\n项目是什么：待补充。\n\n项目目标：待补充。\n\n目标用户：待补充。\n\n技术栈：待补充。\n",
    "MEMORY.md": "# Memory\n\n- Project Copilot 已初始化项目记忆系统。\n",
    "ROADMAP.md": "# Roadmap\n\n## v0.1\n\n- [ ] 项目初始化\n- [ ] 项目记忆\n- [ ] 项目状态分析\n- [ ] 开发会话管理\n- [ ] OSS 准备度检查\n- [ ] 自然语言工作流\n",
    "STATUS.md": "# Status\n\n当前阶段：初始化。\n\n已完成功能：待分析。\n\n进行中功能：待分析。\n\n下一步任务：运行项目检查。\n",
    "DECISIONS.md": "# Decisions\n\n## ADR-0001: v0.1 使用规则驱动\n\n原因：MVP 不依赖外部 API，优先保证本地可运行。\n",
    "WORKFLOW.md": "# Workflow\n\n自然语言意图会被映射为项目工作流，例如初始化、继续开发、检查项目、结束工作和 OSS 检查。\n",
    "USER_PROFILE.md": "# User Profile\n\n- 用户不需要掌握命令行细节。\n- 优先自然语言。\n- 优先中文。\n- 优先开源友好。\n",
}


@dataclass(frozen=True)
class MemoryStore:
    root: Path

    @property
    def ai_dir(self) -> Path:
        return self.root / ".ai"

    def ensure(self) -> list[Path]:
        self.ai_dir.mkdir(exist_ok=True)
        written: list[Path] = []
        for name, content in MEMORY_FILES.items():
            path = self.ai_dir / name
            if not path.exists():
                path.write_text(content, encoding="utf-8")
                written.append(path)
        return written

    def read(self, name: str) -> str:
        path = self.ai_dir / name
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def append_memory(self, text: str) -> None:
        self.ensure()
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with (self.ai_dir / "MEMORY.md").open("a", encoding="utf-8") as handle:
            handle.write(f"\n- {stamp}: {text}\n")

    def update_status(self, content: str) -> None:
        self.ensure()
        (self.ai_dir / "STATUS.md").write_text(content, encoding="utf-8")
