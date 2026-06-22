# Status

更新日期：2026-06-22

当前阶段：可持续开发

当前状态：

- 版本：`0.3.1`
- 当前定位：Codex 项目记忆层
- 当前记忆健康：需要收敛 legacy `HYPOTHESES.md`、`WORKLOG.md` 和 `metrics.md`
- 当前测试结果：`pytest -q` 通过，61 passed

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
- P2 治理能力：README Drift Check、ADR Governance、Session Quality、Legacy Migration Report 和 Multi-Project Validation。
- 项目复盘、项目决策与里程碑时间轴、项目偏航检查和 ADR-first 决策记录。
- Memory Health Summary。
- `.ai/KNOWLEDGE.md`、`.ai/history/`，以及自动派生指标 `.ai/derived/metrics.json`。
- Session Memory：开始工作恢复上下文，结束工作确认候选事件。
- 无参数交互式 CLI 保留为兼容入口。
- unknown intent 中文建议。
- 可编辑安装、`--version` 和 `doctor` 诊断命令。
- Demo 脚本、终端动画和架构图文档。
- GitHub Actions CI 覆盖 Python 3.10、3.11、3.12。
- 面向普通用户的一行安装脚本。

已停止方向：

- 不再继续发展 GitHub sync workflow。
- 不再继续发展 release workflow。
- 不再继续发展 OSS 准备 workflow。
- 不再强化 command system；自然语言意图是主要入口。
- 不再把 `show_roadmap` 作为独立 Roadmap 读取 workflow。
- 不再把 `check_project` 表述为 Project Health Score。

当前验证重点：

- 验证 Project Copilot 是否能作为 Codex 项目的记忆层，而不是抢占日常入口。
- 验证 Charter、ADR、Session Archive、Active Candidates、Roadmap 和 Memory Health 是否能成为跨项目价值指标。
- 验证用户是否可以只打开 Codex 并通过 `.ai` 获得连续项目上下文。
- 验证价值优先，不新增复杂 AI 能力、不接外部 AI API、不开发 Web UI。

当前风险：

- 历史文档、demo、release notes、`HYPOTHESES.md`、`WORKLOG.md` 和 `metrics.md` 中仍保留旧版叙事，需要逐步归档或标注为 legacy。
- 当前主要治理问题已收敛到 legacy 迁移未完成，`WORKLOG.md`、`HYPOTHESES.md` 和 `metrics.md` 仍会持续触发记忆漂移信号。

下一步任务：

- 继续清理历史文档中的命令系统、GitHub/release/OSS 执行型叙事。
- 继续压缩 legacy 文件的活跃内容，推动 Legacy Migration 从“迁移未完成”收敛到纯兼容层。
