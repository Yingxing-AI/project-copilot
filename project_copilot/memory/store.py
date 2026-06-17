from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


MEMORY_FILES = {
    "PROJECT_CONTEXT.md": "# Project Context\n\n项目使命：待确认。\n\n目标用户：待确认。\n\n商业目标：待确认。\n\nMVP 范围：待确认。\n\n技术栈：待确认。\n\n说明：这里记录长期稳定背景，极少修改；不要写临时状态。\n",
    "MEMORY.md": "# Memory\n\n## 长期事实\n\n- Project Copilot 已开始记录项目历史。\n\n## 重要事件\n\n暂无。\n\n## 关键里程碑\n\n暂无。\n\n## 不应遗忘的信息\n\n暂无。\n",
    "ROADMAP.md": "# Roadmap\n\n## Backlog\n\n- [ ] 明确项目目标\n- [ ] 明确目标用户\n- [ ] 明确最小可交付版本\n\n## In Progress\n\n暂无。\n\n## Done\n\n暂无。\n",
    "STATUS.md": "# Status\n\n当前阶段：初始化。\n\n当前重点：完善项目背景。\n\n当前目标：明确 MVP 范围。\n\n当前风险：暂无。\n",
    "DECISIONS.md": "# Decisions\n\n## 决策记录\n\n暂无关键决策。\n\n说明：只追加，不覆盖历史。\n",
    "WORKLOG.md": "# Worklog\n\n说明：按日期追加，记录今日完成、问题和明日计划；不要覆盖历史。\n\n暂无工作记录。\n",
    "KNOWLEDGE.md": "# Knowledge\n\n## 学到的最佳实践\n\n暂无。\n\n## 参考的开源项目\n\n暂无。\n\n## 产品认知\n\n暂无。\n\n## 社区反馈\n\n暂无。\n\n## 重要经验\n\n暂无。\n",
    "metrics.md": "# Metrics\n\n项目创建时间：待确认。\n\n已运行天数：待分析。\n\n决策数量：0\n\n里程碑数量：0\n\n健康度变化：暂无。\n\n偏航指数：待分析。\n",
    "WORKFLOW.md": "# Workflow\n\nProject Copilot 负责记录、提醒、复盘和归档；Codex 负责开发实现。\n",
    "USER_PROFILE.md": "# User Profile\n\n- 用户不需要掌握命令行细节。\n- 优先自然语言。\n- 优先中文。\n- 优先秘书式提醒。\n",
}


@dataclass(frozen=True)
class MemoryStore:
    root: Path

    @property
    def ai_dir(self) -> Path:
        return self.root / ".ai"

    def ensure(self) -> list[Path]:
        self.ai_dir.mkdir(exist_ok=True)
        history_dir = self.ai_dir / "history"
        history_dir.mkdir(exist_ok=True)
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
