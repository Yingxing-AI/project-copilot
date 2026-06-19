from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


MEMORY_FILES = {
    "PROJECT_CHARTER.md": "# Project Charter\n\n项目名称：待确认。\n\n项目使命：待确认。\n\n目标用户：待确认。\n\n商业目标：待确认。\n\nMVP 范围：待确认。\n\n非目标：待确认。\n\n技术栈：待确认。\n\n说明：这里记录长期稳定边界，极少修改；不要写临时状态。\n",
    "PROJECT_CONTEXT.md": "# Project Context\n\n项目使命：待确认。\n\n目标用户：待确认。\n\n商业目标：待确认。\n\nMVP 范围：待确认。\n\n技术栈：待确认。\n\n说明：这里记录长期稳定背景，极少修改；不要写临时状态。\n",
    "MEMORY.md": "# Memory\n\n## 长期事实\n\n- Project Copilot 已开始记录项目历史。\n\n## 重要事件\n\n暂无。\n\n## 关键里程碑\n\n暂无。\n\n## 不应遗忘的信息\n\n暂无。\n",
    "HYPOTHESES.md": "# Hypotheses\n\n## 待验证假设\n\n暂无。\n\n## 待确认推测\n\n暂无。\n\n说明：这里记录未确认的判断、待验证的分析和低置信度结论，不要写成事实或决策。\n",
    "ROADMAP.md": "# Roadmap\n\n## Backlog\n\n- [ ] 明确项目目标\n- [ ] 明确目标用户\n- [ ] 明确最小可交付版本\n\n## In Progress\n\n暂无。\n\n## Done\n\n暂无。\n",
    "STATUS.md": "# Status\n\n当前阶段：初始化。\n\n当前重点：完善项目背景。\n\n当前目标：明确 MVP 范围。\n\n当前风险：暂无。\n",
    "DECISIONS.md": "# Decisions\n\n说明：旧版决策索引。新决策优先写入 `.ai/adr/`，本文件只保留兼容摘要。\n\n暂无关键决策。\n",
    "WORKLOG.md": "# Worklog\n\n说明：兼容旧版工作日志。Session Memory 模式下，普通开发流水不再自动写入；重要会话摘要归档到 `.ai/sessions/archive/`。\n\n暂无工作记录。\n",
    "KNOWLEDGE.md": "# Knowledge\n\n## 学到的最佳实践\n\n暂无。\n\n## 参考的开源项目\n\n暂无。\n\n## 产品认知\n\n暂无。\n\n## 社区反馈\n\n暂无。\n\n## 重要经验\n\n暂无。\n",
    "metrics.md": "# Metrics\n\n项目创建时间：待确认。\n\n已运行天数：待分析。\n\n决策数量：0\n\n里程碑数量：0\n\n健康度变化：暂无。\n\n偏航指数：待分析。\n\n说明：这是辅助指标快照，优先由状态与历史文件派生，不要把它当作事实源。\n",
}

ADR_INDEX = "# ADR Index\n\n说明：记录三个月后仍重要的架构、产品范围和长期取舍。普通代码修改、测试和小型 Bug 修复不进入 ADR。\n\n暂无 ADR。\n"

SESSION_CURRENT = "# Current Session\n\n## 候选事件\n\n说明：开发过程中只收集候选事件，结束工作时由用户确认后再写入长期记忆。\n\n### ADR 候选\n\n暂无。\n\n### 里程碑候选\n\n暂无。\n\n### 风险候选\n\n暂无。\n\n### 知识候选\n\n暂无。\n"


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
        adr_dir = self.ai_dir / "adr"
        adr_dir.mkdir(exist_ok=True)
        sessions_dir = self.ai_dir / "sessions"
        sessions_dir.mkdir(exist_ok=True)
        archive_dir = sessions_dir / "archive"
        archive_dir.mkdir(exist_ok=True)
        written: list[Path] = []
        for name, content in MEMORY_FILES.items():
            path = self.ai_dir / name
            if not path.exists():
                path.write_text(content, encoding="utf-8")
                written.append(path)
        adr_index = adr_dir / "index.md"
        if not adr_index.exists():
            adr_index.write_text(ADR_INDEX, encoding="utf-8")
            written.append(adr_index)
        session_current = sessions_dir / "current.md"
        if not session_current.exists():
            session_current.write_text(SESSION_CURRENT, encoding="utf-8")
            written.append(session_current)
        return written

    def read_session_candidates(self) -> str:
        self.ensure()
        return (self.ai_dir / "sessions" / "current.md").read_text(encoding="utf-8")

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

    def append_hypothesis(self, text: str) -> None:
        self.ensure()
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with (self.ai_dir / "HYPOTHESES.md").open("a", encoding="utf-8") as handle:
            handle.write(f"\n- {stamp}: {text}\n")

    def append_session_candidate(self, category: str, text: str) -> None:
        self.ensure()
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with (self.ai_dir / "sessions" / "current.md").open("a", encoding="utf-8") as handle:
            handle.write(f"\n- {stamp} [{category}] {text}\n")

    def update_status(self, content: str) -> None:
        self.ensure()
        (self.ai_dir / "STATUS.md").write_text(content, encoding="utf-8")
