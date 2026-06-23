# Decisions

## 2026-06-16

- 决策：当前版本使用规则驱动。
- 原因：MVP 不依赖外部 API，优先保证本地可运行。
- 影响：秘书提醒、复盘和偏航检查先使用本地规则实现。

## 2026-06-17

- 决策：进入 Sprint Secretary UX，把 Project Copilot 定位为 Codex 项目的项目秘书。
- 原因：第一优先级是优化非工程用户体验，而不是增加开发或 AI 能力。
- 影响：命令、文案和输出格式优先使用“记录、提醒、复盘、归档、守护”的表达。

## 2026-06-17

- 决策：首次项目建档改为方案驱动，默认不再使用三问式问卷。
- 原因：用户通常可以一次性提供完整项目方案，先分析完整输入再追问缺失项更符合秘书式体验，也能减少打断。
- 影响：`init` 和首次交互需要先提取项目使命、目标用户、商业目标、MVP 范围、技术栈、当前阶段、初始 Roadmap 和初始 Decisions；只有缺失关键信息时才追问。

## 2026-06-17

- 决策：将项目记忆分层为事实、假设、计划和决策，并新增 `HYPOTHESES.md`。
- 原因：`continue`、收工、复盘和决策记录会自然产生推测与中间判断，必须与长期事实和已确认决策分开，才能避免项目记忆污染。
- 影响：`MEMORY.md` 只记录稳定事实，`HYPOTHESES.md` 记录未确认判断，`WORKLOG.md` 只记录实际完成工作，`DECISIONS.md` 只记录已确认取舍，`continue` 变为只读恢复入口，不再自动扩展规划。

## 2026-06-17

- 决策：`sync_project_state` 和 `review_project` 不再向 `MEMORY.md` 追加维护型流水。
- 原因：同步状态和生成复盘归档本身是维护动作，不是稳定事实；把这些动作写进长期记忆会增加噪音并模糊事实边界。
- 影响：长期事实层只保留真正的项目历史和稳定认知，维护性动作改由状态文件、复盘归档和工作日志承载。

## 2026-06-17

- 决策：初始化和接管流程不再把用户原始输入全文写入 `MEMORY.md`。
- 原因：原始输入通常包含大量临时上下文和方案细节，不应被当成长期事实直接保存。
- 影响：`MEMORY.md` 只记录初始化和接管这类事件的短摘要，详细方案仍由 `PROJECT_CONTEXT.md`、`STATUS.md`、`ROADMAP.md` 和 `DECISIONS.md` 承载。

## 2026-06-17

- 决策：`record_decision` 只写 `DECISIONS.md`，不再把已确认决策复制进 `MEMORY.md`。
- 原因：决策已经由 `DECISIONS.md` 作为唯一事实来源承载，重复写入长期事实层会制造噪音并降低边界清晰度。
- 影响：`MEMORY.md` 继续只保留项目历史中的真实事件摘要，不再重复记录决策文本。

## 2026-06-18

- 决策：删除 `.ai/WORKFLOW.md` 和 `.ai/USER_PROFILE.md`，并将 `metrics.md` 降级为辅助指标快照。
- 原因：这两层没有形成稳定消费面，继续保留会扩大记忆面并制造职责重叠；`metrics.md` 如果不能作为派生层维护，就不应继续充当核心事实层。
- 影响：`.ai/` 只保留核心事实、假设、决策、工作日志、知识沉淀和月归档；文档与代码需要同步收敛到这套核心结构。

## 2026-06-18

- 决策：工作流入口按 Git 仓库顶层归一化项目根目录，避免在子目录或错误工作目录下污染其他项目的 `.ai/` 文件。
- 原因：跨项目运行时，cwd 并不总是项目根；如果直接用 cwd 写 `.ai`，很容易把记忆文件落到错误层级。
- 影响：`project-copilot` 的 CLI 和 workflow 调度会优先将路径收敛到 `git rev-parse --show-toplevel` 返回的仓库根，再进行记忆写入。

日期：2026-06-19

决策：Project Copilot 收敛为 Codex 项目记忆层，停止继续发展 GitHub sync、release、OSS 准备和命令式执行工作流。

原因：Codex 负责开发，Git 负责版本管理，Project Copilot 负责项目记忆；继续强化执行型工作流会与 Codex 原生能力重复。

影响：新增 `.ai/adr/` 和 `.ai/sessions/`；新决策优先进入 ADR；开发过程中不自动扩写长期记忆，结束工作时统一确认候选事件。

日期：2026-06-19

决策：验证报告跟随长期记忆写入和验证快照导出自动刷新，手动刷新仅作为兼容和修复命令保留。

原因：Validation 应是项目记忆层的自然副产品，不能要求用户额外维护，也不能让 Session 候选污染派生统计。

影响：`export_validation_snapshot` 导出快照后会同步刷新 `docs/validation-report.md`；未确认假设和 Session 候选不触发刷新。

日期：2026-06-19

决策：执行 P0 记忆架构收敛，引入 `PROJECT_CHARTER.md`，将确认决策改为 ADR-first，将复盘改为只读，将同步状态降级为 validation 派生刷新。

原因：测试、Git、Release、Changelog 和普通项目管理总结属于 Codex/Git；Project Copilot 应只维护长期项目记忆和派生验证。

影响：`init_project` 不再自动 `git init`；`record_decision` 写入 `.ai/adr/`；未确认决策进入 `.ai/sessions/current.md`；`review_project` 不再写 `history/`；`sync_project_state` 不再运行测试或同步 README/Roadmap/Changelog/AGENTS。

日期：2026-06-19

决策：执行 P1 Memory View 收敛，将 `check_project` 改为 Memory Health，`show_roadmap` 降级为兼容别名，`timeline_project` 改为 ADR/history/session 派生视图，并将指标改为 derived metrics。

原因：剩余 workflow 仍带有旧 Secretary UX、项目健康度和工作日志时间轴叙事，容易与 Codex 原生开发能力和 Git 记录职责重叠。

影响：详见 ADR 0006：`.ai/adr/0006-memory-view-convergence.md`。本文件仅保留兼容索引。

日期：2026-06-20

决策：在 Validation 链路中引入 Memory Governance 与 Drift Detection，统一派生 README Drift、ADR Governance、Session Quality、Legacy Migration 和 Multi-Project Validation。

原因：仅有记忆结构还不足以证明长期价值；如果 README、ADR、Session Archive 和 legacy 文件缺少持续治理，`.ai` 会重新漂移。

影响：详见 ADR 0007：`.ai/adr/0007-memory-governance-and-drift-detection.md`。Validation 从单纯统计扩展为治理视图，但不自动修改 README、不自动删除 legacy 文件，也不引入 AI 评分。

日期：2026-06-23

决策：将 `.ai/validation.json` 明确定义为可覆盖的 Validation Snapshot，并约束 `derived/metrics.json` 与 `docs/validation-report.md` 的单向派生关系。

原因：beta.3 已形成 Validation 派生链路，但仍缺少 snapshot 生命周期治理，容易把 report 或快照误当成事实来源。

影响：详见 ADR 0008：`.ai/adr/0008-validation-snapshot-lifecycle.md`。允许刷新与禁止刷新的触发条件被显式化；`validation.json` 不是长期记忆源，report 也不得反向修改真实 `.ai`。
