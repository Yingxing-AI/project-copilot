# Project Charter

项目名称：Project Copilot

项目使命：作为 Codex 的长期项目记忆层，帮助 Codex 持续理解项目为什么存在、为什么这样设计、哪些能力被放弃、项目如何演化。

目标用户：

- 创业者。
- 产品经理。
- 业务人员。
- AI Coding 新手。
- 使用 Codex 开发项目的非专业开发者。

商业目标：让非专业开发者能长期维护 AI Coding 项目上下文，不需要记住工程术语和历史细节。

MVP 范围：

- 本地 `.ai` 项目记忆结构。
- Project Charter。
- ADR。
- Session Memory。
- 上下文恢复。
- MVP/目标用户/历史决策偏航提醒。
- 从真实 `.ai` 派生 validation。

非目标：

- 不负责写代码。
- 不负责测试执行。
- 不负责 Git、Commit、Push、Tag、Release。
- 不负责 Changelog 生成。
- 不负责 OSS 准备 workflow。
- 不做 MCP。
- 不做 AI Provider。
- 不做插件系统。

技术栈：

- Python 3.10+
- setuptools packaging
- pytest
- 规则驱动 intent classifier
- 本地文件系统 `.ai/` 项目记忆

说明：这里记录长期稳定边界，极少修改；不要写临时状态。

