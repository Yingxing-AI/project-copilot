# ADR 0005: 执行 P0 记忆架构收敛

日期：2026-06-19

状态：Accepted

背景：

Project Copilot 已收敛为 Codex 的长期项目记忆层，但仍有 P0 级重合和写入边界问题：`sync_project_state` 仍执行测试、读取 Git、同步 Changelog；`record_decision` 仍写旧 `DECISIONS.md`；`review_project` 会自动写入 `history/`；项目定义层仍使用泛化的 `PROJECT_CONTEXT.md`。

决策：

执行 P0 收敛：引入 `PROJECT_CHARTER.md`，移除 `init_project` 的自动 Git 初始化，`record_decision` 改为 ADR-first，未确认决策进入 Session 候选，`review_project` 改为只读预览，`sync_project_state` 降级为只刷新 validation 派生数据。

原因：

Codex 负责代码、测试、Git、Commit、Push、Release 和 Changelog。Project Copilot 只负责项目定义、项目记忆、ADR、上下文恢复、偏航提醒和记忆质量验证。

取舍：

获得更清晰的产品边界和更少的过度写入。放弃由 Project Copilot 自动维护测试基线、Git 元信息、Changelog 和复盘归档。

影响：

新项目会生成 `PROJECT_CHARTER.md`。确认决策会写入 `.ai/adr/` 并在 `DECISIONS.md` 保留兼容索引。复盘不再自动归档。同步状态不再运行测试、不读取 Git、不修改 README、ROADMAP、CHANGELOG 或 AGENTS。

