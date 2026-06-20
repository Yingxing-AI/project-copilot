# ADR 0007: 引入 Memory Governance 与 Drift Detection

日期：2026-06-20

状态：Accepted

背景：

P0 和 P1 已完成项目记忆层收敛，但仅有 Charter、ADR、Session Memory 和 Validation 还不足以证明长期价值。README 已出现漂移，legacy 文件仍保留，ADR 与 Session Archive 也缺少持续治理规则。如果不把这些问题显式纳入派生验证，项目记忆层会重新退化为“有结构但无人治理”的静态目录。

决策：

在现有 Validation 链路上引入规则化的 Memory Governance 与 Drift Detection，统一派生以下治理视图：README Drift Check、ADR Governance、Session Quality、Legacy Migration Report 和 Multi-Project Validation。

原因：

Project Copilot 的长期价值不在于继续扩展新 workflow，而在于证明 `.ai` 记忆层被真实使用、持续收敛、能够发现漂移并指导迁移。把治理能力做成从真实 `.ai` 自动派生的数据，才能避免再维护一套脱离项目现实的元文档。

取舍：

获得可持续的文档漂移检测、ADR 生命周期治理、Session Archive 质量约束、legacy 迁移进度可视化和跨项目统一统计。放弃依赖人工检查 README、人工点检 ADR、人工维护 validation-report 或引入复杂 AI 评分。

影响：

- README Drift 只报告 README 与 Charter、ADR、Session Archive、Validation、Memory Health 的冲突和缺口，不自动修改 README。
- ADR Governance 负责检查编号冲突、状态缺失、非法状态值和 `Superseded By` 链断裂。
- Session Quality 只做规则化检查，关注过长、过短、ADR 重复和噪音过高，不引入主观评分模型。
- Legacy Migration Report 只评估 `PROJECT_CONTEXT.md`、`WORKLOG.md`、`HYPOTHESES.md`、`metrics.md`、`DECISIONS.md` 的迁移状态，不自动删除文件。
- Multi-Project Validation 通过 `validation/sources.yaml` 维护项目列表，统一输出跨项目 Validation Summary，不再手工维护 validation-report。
