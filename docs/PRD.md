# Project Copilot v0.1 产品需求文档

Project Copilot 是一个面向 AI Coding 场景的自然语言项目操作系统。

目标用户无需掌握 Git、Docker、Python、前端开发、后端开发或项目管理工具，只需要通过自然语言表达意图，即可完成项目创建、开发、维护、发布和开源运营。

## MVP 目标

- 项目初始化
- 已有项目接管
- 项目记忆
- 项目状态分析
- 开发会话管理
- 开源项目检查
- 自然语言工作流

## 第一版自然语言意图

- 开始一个新项目
- 接管已有项目
- 继续开发
- 检查项目
- 今天结束工作
- 生成路线图
- 检查 OSS 准备度
- 准备开源
- 开源到 GitHub
- 私有同步到 GitHub
- 准备发布
- 今天做了什么
- 下一步做什么
- 总结项目

## 技术架构

Python 3.10+，v0.1 使用规则驱动和本地分析，不依赖外部 API。

## Workflow 调度层

自然语言意图先进入 `intent` 识别，输出标准 `intent_name`。`workflow` engine 负责注册和分发工作流，CLI 不直接调用具体功能模块。

第一阶段工作流：

- `init_project`
- `check_project`
- `continue_development`
- `close_day`
- `oss_check`
- `prepare_oss`
- `github_sync`

## GitHub 同步

Project Copilot 需要支持两种发布目标：

- 公开开源：创建或连接 public GitHub 仓库，补齐 OSS 文件并推送。
- 私有同步：创建或连接 private GitHub 仓库，用于个人或团队私有项目备份与协作。

第一阶段先实现同步计划和前置条件检查，包括 Git 状态、remote、GitHub CLI、仓库地址和目标可见性。后续版本继续补齐自动创建仓库、自动 push、release 和 changelog。

## 已有项目接管

对于已经开发到一半的项目，Project Copilot 应采用非破坏式接管：

- 不覆盖已有 README、LICENSE、源码和文档
- 扫描技术栈、目录结构、测试、文档和 Git 状态
- 生成 `.ai/PROJECT_CONTEXT.md`
- 生成 `.ai/STATUS.md`
- 在 `.ai/MEMORY.md` 记录接管事件
- 将不确定信息标记为待确认
