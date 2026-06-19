# ADR 0006: 收敛 Memory View 工作流

日期：2026-06-19

状态：Accepted

背景：

P0 已移除 Git、Release、OSS 和过度写入边界问题，但 `show_roadmap`、`timeline_project`、`check_project`、`HYPOTHESES.md`、`WORKLOG.md` 和 `metrics.md` 仍保留旧 Secretary UX 与工程健康度叙事。

决策：

执行 P1 Memory View 收敛：`check_project` 改为 Memory Health Summary，`show_roadmap` 降级为 `check_project` 兼容别名，`timeline_project` 优先展示 ADR、history 和 Session Archive，`HYPOTHESES.md` 停止主动写入，`WORKLOG.md` 降级为 legacy，指标改由 `.ai/derived/metrics.json` 自动派生。

原因：

Project Copilot 不应重复 Codex 的开发、测试、Git 或项目管理能力。它的价值是让 Codex 能恢复长期上下文、理解历史取舍，并识别记忆层是否漂移。

取舍：

保留旧 intent 和旧文件以降低兼容风险，但不再强化这些入口的独立产品心智。Validation 报告从工作日志、决策和知识数量转向 Charter、ADR、Session Archive、Active Candidates、Roadmap 和 Memory Health。

影响：

新项目不再主动创建 `.ai/metrics.md`，但旧项目中的 `metrics.md` 不删除。`show_roadmap` 用户输入仍可用，但输出 Memory Health。旧 `DECISIONS.md` 只作为兼容统计来源，ADR 数只统计 `.ai/adr/`。
