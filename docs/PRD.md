# Project Copilot 产品需求文档

Project Copilot 是 Codex 项目的项目秘书。

Codex 负责开发，Project Copilot 负责记住：项目档案、决策记录、项目时间轴、项目复盘、偏航提醒和知识沉淀。

目标用户是创业者、产品经理、业务人员、AI Coding 新手和非专业开发者。用户不需要掌握 Git、Docker、Python、前端开发、后端开发或项目管理工具，只需要通过中文表达项目管理意图。

## MVP 目标

- 方案驱动项目初始化
- 已有项目接管
- 项目记忆
- 项目状态卡片
- 项目复盘
- 项目时间轴
- 项目偏航检查
- 决策记录
- 知识沉淀
- 开发会话管理
- 中文优先自然语言工作流

## 第一版自然语言意图

- 开始一个新项目
- 接管已有项目
- 继续开发
- 项目状态
- 今天结束工作
- 项目复盘
- 项目时间轴
- 项目偏航检查
- 记录决策
- 查看路线图
- 保存进度
- 备份到云端
- 发布版本
- 今天做了什么
- 下一步做什么
- 总结项目

## 技术架构

Python 3.10+，当前版本使用规则驱动和本地分析，不依赖外部 API。

## Workflow 调度层

自然语言意图先进入 `intent` 识别，输出标准 `intent_name`。`workflow` engine 负责注册和分发工作流，CLI 不直接调用具体功能模块。

核心工作流：

- `init_project`
- `check_project`
- `continue_development`
- `close_day`
- `review_project`
- `timeline_project`
- `drift_check`
- `record_decision`
- `show_roadmap`

## 秘书提醒

Project Copilot 在启动、检查项目和偏航检查时主动提醒：

- 距离上次复盘过久
- Roadmap 长时间未更新
- 新增需求超出 MVP
- 新方向偏离目标用户
- 新决策与历史决策冲突

用户界面不展示算法、治理、ADR 等技术术语，只展示“提醒”“风险”“请选择”。

## 已有项目接管

对于已经开发到一半的项目，Project Copilot 应采用非破坏式接管：

- 不覆盖已有 README、LICENSE、源码和文档
- 扫描技术栈、目录结构、测试、文档和 Git 状态
- 生成 `.ai/PROJECT_CONTEXT.md`
- 生成 `.ai/STATUS.md`
- 在 `.ai/MEMORY.md` 记录接管事件摘要
- 将不确定信息标记为待确认

## 与 Codex 的边界

Codex 是开发工程师，负责写代码、测试、实现功能和修 Bug。

Project Copilot 是项目秘书，负责记录、提醒、复盘、归档和守护项目方向。
