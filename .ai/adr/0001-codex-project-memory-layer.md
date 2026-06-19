# ADR 0001: 收敛为 Codex 项目记忆层

日期：2026-06-19

状态：Accepted

背景：

Project Copilot 早期同时包含项目秘书、命令系统、GitHub 同步、发布、OSS 准备等工作流。这些能力和 Codex、Git、GitHub 的原生职责存在重叠，会稀释产品定位。

决策：

Project Copilot 收敛为 Codex 项目记忆层，负责帮助 Codex 持续记住项目背景、MVP 边界、关键决策原因和长期知识。

原因：

Codex 负责开发，Git 负责版本管理，Project Copilot 负责项目记忆。这样可以避免重复 Codex 原生能力，并让非专业用户只感受到 Codex 更懂项目。

取舍：

获得更清晰的边界和更低的维护复杂度。放弃继续围绕 commit、push、release、测试、代码修改、GitHub 同步和 OSS 准备设计 Project Copilot workflow。

影响：

Intent 和 workflow 将停止强化命令体系，执行型 GitHub/release/OSS 工作流从核心产品中移除。文档、Roadmap 和 `.ai` 结构围绕项目记忆重新收敛。

