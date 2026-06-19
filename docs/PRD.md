# Project Copilot 产品需求文档

Project Copilot 是 Codex 项目的项目记忆层。

Codex 负责开发，Git 负责版本管理，Project Copilot 负责让 Codex 持续记住：项目使命、目标用户、MVP 边界、关键 ADR、重要里程碑、长期风险和产品认知。

目标用户是创业者、产品经理、业务人员、AI Coding 新手和非专业开发者。用户不需要掌握 Git、Docker、Python、前端开发、后端开发或项目管理工具，只需要自然表达项目意图。

## MVP 目标

- 方案驱动项目初始化
- 已有项目接管
- 项目记忆
- Project Charter
- Session Memory
- ADR 记录
- 项目状态恢复
- 项目复盘
- 项目时间轴
- 项目偏航检查
- 知识沉淀
- 中文优先自然语言意图
- 从真实 `.ai` 自动派生验证数据

## 非目标

- 不做 MCP
- 不做 AI Provider
- 不做插件系统
- 不做 commit workflow
- 不做 push workflow
- 不做 release workflow
- 不做测试执行 workflow
- 不做代码修改 workflow
- 不做 GitHub sync workflow
- 不做 OSS 准备 workflow

## 第一版自然语言意图

- 开始一个新项目
- 接管已有项目
- 继续开发
- 项目现在怎么样
- 最近发生了什么
- 这个想法靠谱吗
- 今天结束工作
- 项目复盘
- 项目时间轴
- 项目偏航检查
- 记录决策
- 查看路线图
- 总结项目
- 导出验证快照
- 刷新验证报告

## Session Memory

开始工作：

- 读取 `.ai`
- 恢复项目上下文

开发过程中：

- 不自动写长期文件
- 不自动扩写 Roadmap
- 不自动扩写 Memory
- 不自动扩写 Worklog
- 只维护会话级候选事件

结束工作：

- 展示 ADR 候选、里程碑候选、风险候选、知识候选
- 用户确认哪些内容三个月后仍重要
- 统一写入长期记忆

## Validation 自动刷新

验证数据是项目记忆层的自然副产品，不要求用户维护单独 case study。

自动刷新触发点：

- 初始化项目
- 接管已有项目
- 写入已确认决策
- 同步项目状态
- 导出验证快照
- 结束工作后，如果用户确认并写入长期记忆

不刷新触发点：

- 继续开发只读恢复上下文
- 开发过程中的 Session 候选事件
- 未确认假设
- 普通代码修改、测试增加、小型 Bug 修复

手动刷新只作为兼容和修复命令保留。

## ADR

新决策优先写入 `.ai/adr/`。

`DECISIONS.md` 保留旧版兼容摘要，不再作为所有新决策的唯一承载文件。

## 技术架构

Python 3.10+，当前版本使用规则驱动和本地分析，不依赖外部 API。

自然语言意图先进入 `intent` 识别，输出标准 `intent_name`。`workflow` engine 负责注册和分发记忆工作流，CLI 不直接调用具体功能模块。

核心工作流：

- `init_project`
- `adopt_project`
- `check_project`
- `continue_development`
- `close_day`
- `review_project`
- `timeline_project`
- `drift_check`
- `record_decision`
- `show_roadmap`（兼容别名，实际进入 Memory Health）
- `export_validation_snapshot`
- `refresh_validation_report`

## 与 Codex 的边界

Codex 是开发工程师，负责写代码、测试、实现功能、修 Bug、commit、push 和 release。

Project Copilot 是项目记忆层，负责记录为什么这样做、提醒边界、恢复上下文和沉淀长期知识。

P0 边界：

- `sync_project_state` 不运行测试、不读取 Git、不同步 Changelog。
- `record_decision` 写 ADR，不再把新决策只追加到 `DECISIONS.md`。

P1 边界：

- `check_project` 输出 Memory Health Summary，不再输出 Project Health Score。
- `timeline_project` 优先展示 ADR、history 和 Session Archive。
- `show_roadmap` 不再作为独立路线图读取 workflow。
- `review_project` 是只读派生视图，不自动写归档。
- `init_project` 不自动初始化 Git。
