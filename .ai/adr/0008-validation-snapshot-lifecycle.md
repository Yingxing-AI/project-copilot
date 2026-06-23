# ADR 0008: 定义 Validation Snapshot 生命周期

日期：2026-06-23

状态：Accepted

背景：

beta.3 已将 Validation 收敛为从真实 `.ai` 自动派生的治理视图，但现有规则只明确了 Validation Report 的刷新时机，没有明确 `.ai/validation.json`、`.ai/derived/metrics.json` 和 `docs/validation-report.md` 的生命周期边界。实现层已经会覆盖写入这些文件，如果不把写入边界显式化，Validation 会继续停留在“可工作但规则不完整”的治理灰区。

决策：

`.ai/validation.json` 定义为从真实 `.ai` 记忆文件派生的可覆盖快照，不是长期记忆源；唯一事实来源仍是 `PROJECT_CHARTER.md`、`STATUS.md`、`ROADMAP.md`、`MEMORY.md`、`KNOWLEDGE.md`、`adr/`、`sessions/archive/` 及其兼容层。`validation.json` 允许覆盖生成，但不允许通过手工编辑反向成为事实输入。`.ai/derived/metrics.json` 必须与 `validation.json` 同批刷新。`docs/validation-report.md` 是可重建视图，只能由真实 `.ai` 或 `validation.json` 快照派生，不得反向修改真实记忆。

原因：

Validation 的价值在于提供统一治理视图，而不是增加新的事实层。只有把 Validation 明确为派生层，才能同时满足 Session Memory 的低写入原则、避免普通开发流水污染长期记忆，并保持 report、metrics 和 snapshot 之间的因果方向单向明确。

取舍：

获得清晰的派生数据生命周期、可覆盖快照语义和更稳定的治理边界。放弃把 `validation.json` 当成可人工维护的事实文件，也放弃让 `docs/validation-report.md` 充当隐式项目来源。

影响：

- 允许刷新 `validation.json` 的触发条件只有：`init_project`、`adopt_project`、已确认 ADR 写入之后、结束工作且已确认写入 Session Archive 或长期记忆之后、`sync_project_state`、`export_validation_snapshot`，以及 `refresh_validation_report` 作为兼容或修复入口。
- 禁止刷新 `validation.json` 的场景包括：`continue_development`、仅修改 Session 候选、未确认假设、普通代码/测试/文档修改、未改变真实 `.ai` 记忆语义的开发流水，以及结束工作但只形成候选且没有确认长期写入。
- `refresh_validation_report` 可以重建 `docs/validation-report.md`，但不得让 report 反向成为真实记忆的事实来源。
- `validation.json` 与 `derived/metrics.json` 的写入必须保持同批完成，避免派生视图互相漂移。
