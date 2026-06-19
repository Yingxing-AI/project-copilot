# ADR 0002: 使用 Session Memory 写入模型

日期：2026-06-19

状态：Accepted

背景：

持续读写 `.ai` 会导致 ROADMAP 膨胀、WORKLOG 膨胀和 MEMORY 污染。普通代码修改、测试增加、小型 Bug 修复和临时讨论已经由 Git 或会话上下文承载，不应进入长期项目记忆。

决策：

Project Copilot 使用 Session Memory 模式：开始工作时读取 `.ai` 恢复上下文，开发过程中只维护会话级候选事件，结束工作时统一确认并写入长期记忆。

原因：

项目记忆应该只保存三个月后仍重要的内容，包括架构决策、产品取舍、MVP 范围变化、重要里程碑、长期风险和长期知识。

取舍：

获得更干净的长期记忆和更低的写入噪音。放弃每轮对话自动写状态、Roadmap、Memory 或 Worklog 的模式。

影响：

新增 `.ai/sessions/current.md` 作为候选事件缓冲。`WORKLOG.md` 降级为旧版兼容和重大会话摘要，不再记录普通开发流水。

