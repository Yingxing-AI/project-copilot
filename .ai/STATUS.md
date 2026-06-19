# Status

更新日期：2026-06-19

当前阶段：可持续开发

当前状态：

- 版本：`0.3.0b2`
- 分支：`main`
- 最新提交：`cd63b2d chore: prepare release v0.3.0-beta.2`
- 最新标签：`v0.3.0-beta.2`
- 测试基线：`pytest -q` 通过，53 passed。
- 项目健康度：100/100
- 当前定位：Codex 项目记忆层

已完成功能：

- 自然语言意图识别。
- Workflow engine 注册和分发。
- `.ai/` 项目记忆系统。
- `.ai/adr/` ADR 体系。
- `.ai/sessions/` Session Memory 候选事件结构。
- 项目初始化和已有项目接管。
- Codex Native 主流程：`project-copilot init/adopt` 生成 `.ai/`、`AGENTS.md` 和 `docs/CODEX_WORKFLOW.md`。
- `AGENTS.md` 生成 Codex 维护 `.ai` 项目记忆的规则。
- `docs/CODEX_WORKFLOW.md` 面向用户说明 Project Copilot 与 Codex 的日常协作方式。
- 多项目验证体系：从真实 `.ai/validation.json` 快照自动刷新 `docs/validation-report.md`。
- 项目复盘、项目时间轴、项目偏航检查、记录决策和查看路线图。
- 项目状态分析和健康度评分。
- `.ai/KNOWLEDGE.md`、`.ai/history/`，以及辅助指标 `.ai/metrics.md`。
- Session Memory：开始工作恢复上下文，结束工作确认候选事件。
- 无参数交互式 CLI 保留为兼容入口。
- unknown intent 中文建议。
- 可编辑安装、`--version` 和 `doctor` 诊断命令。
- Demo 脚本、终端动画和架构图文档。
- 自动同步 `.ai/STATUS.md`、Roadmap、Changelog 和 AGENTS managed 区块。
- GitHub Actions CI 覆盖 Python 3.10、3.11、3.12。
- 面向普通用户的一行安装脚本。

已停止方向：

- 不再继续发展 GitHub sync workflow。
- 不再继续发展 release workflow。
- 不再继续发展 OSS 准备 workflow。
- 不再强化 command system；自然语言意图是主要入口。

当前验证重点：

- 验证 Project Copilot 是否能作为 Codex 项目的记忆层，而不是抢占日常入口。
- 验证 ADR、Session 候选和知识沉淀是否能成为跨项目价值指标。
- 验证用户是否可以只打开 Codex 并通过 `.ai` 获得连续项目上下文。
- 验证价值优先，不新增复杂 AI 能力、不接外部 AI API、不开发 Web UI。

当前风险：

- 历史文档、demo 和 release notes 中仍保留旧版 GitHub/release/OSS workflow 叙事，需要逐步归档或标注为历史。

下一步任务：

- 继续清理历史文档中的命令系统、GitHub/release/OSS 执行型叙事。
- 观察 Session Memory 是否能减少 Roadmap、Worklog 和 Memory 膨胀。
