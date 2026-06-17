from __future__ import annotations

from pathlib import Path


def ensure_codex_native_files(root: Path) -> list[Path]:
    docs_dir = root / "docs"
    docs_dir.mkdir(exist_ok=True)

    files = {
        root / "AGENTS.md": render_agents_md(),
        docs_dir / "CODEX_WORKFLOW.md": render_codex_workflow_doc(),
    }
    written: list[Path] = []
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def render_agents_md() -> str:
    return "\n".join(
        [
            "# Agents",
            "",
            "你是 Codex。",
            "你负责开发。",
            "同时你必须维护 `.ai` 项目记忆。",
            "",
            "## 每次开始开发前",
            "",
            "- 阅读 `.ai/PROJECT_CONTEXT.md`",
            "- 阅读 `.ai/STATUS.md`",
            "- 阅读 `.ai/ROADMAP.md`",
            "- 阅读 `.ai/DECISIONS.md`",
            "",
            "## 每次完成开发后",
            "",
            "- 更新 `.ai/STATUS.md`",
            "- 追加 `.ai/WORKLOG.md`",
            "- 必要时追加 `.ai/DECISIONS.md`",
            "- 必要时更新 `.ai/MEMORY.md`",
            "- 必要时更新 `.ai/KNOWLEDGE.md`",
            "- 必要时更新 `.ai/history/YYYY-MM.md`",
            "- 必要时更新 `.ai/metrics.md`",
            "",
            "## 重要规则",
            "",
            "- 不要覆盖历史决策。",
            "- 不要把临时状态写进 `PROJECT_CONTEXT.md`。",
            "- 不要未经用户确认扩大 MVP 范围。",
            "- 如果用户提出超出 MVP 的需求，要提醒。",
            "- 如果新方向与历史决策冲突，要提醒。",
            "- 如果项目长期未复盘，要提醒。",
            "",
            "## 用户表达",
            "",
            "- `commit` = 保存进度",
            "- `push` = 备份到云端",
            "- `release` = 发布版本",
            "- `tag` = 版本标记",
            "",
        ]
    )


def render_codex_workflow_doc() -> str:
    return "\n".join(
        [
            "# Codex Workflow",
            "",
            "Project Copilot 为 Codex 安装持久项目记忆层。日常开发时，用户只需要打开 Codex；Codex 按 `AGENTS.md` 读取和维护 `.ai` 项目记忆。",
            "",
            "## 每天开始",
            "",
            "在项目目录打开：",
            "",
            "```bash",
            "codex",
            "```",
            "",
            "然后可以直接说：",
            "",
            "```text",
            "继续开发这个项目",
            "```",
            "",
            "Codex 应先读取 `.ai` 项目记忆。",
            "",
            "## 开发过程中",
            "",
            "Codex 如果发现：",
            "",
            "- 新需求超出 MVP",
            "- 方向偏离目标用户",
            "- 与历史决策冲突",
            "",
            "应提醒用户确认。",
            "",
            "## 每天结束",
            "",
            "用户说：",
            "",
            "```text",
            "今天结束工作",
            "```",
            "",
            "Codex 应：",
            "",
            "- 总结今日变更",
            "- 更新 `.ai/STATUS.md`",
            "- 追加 `.ai/WORKLOG.md`",
            "- 更新 `.ai/MEMORY.md`",
            "- 必要时更新 `.ai/DECISIONS.md`",
            "",
            "## 每周复盘",
            "",
            "用户说：",
            "",
            "```text",
            "复盘项目",
            "```",
            "",
            "Codex 应读取 `.ai` 文件并输出：",
            "",
            "- 本周完成",
            "- 关键决策",
            "- 风险变化",
            "- Roadmap 推进",
            "- 是否偏航",
            "",
        ]
    )
