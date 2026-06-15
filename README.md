# Project Copilot

Project Copilot 是一个面向 AI Coding 场景的自然语言项目操作系统。

用户不需要记 Git、Docker、Python、前后端或项目管理命令，只需要表达意图：

- `初始化项目`
- `接管已有项目`
- `继续开发项目`
- `检查项目`
- `今天结束工作`
- `检查 OSS 准备度`
- `准备开源`
- `开源到 GitHub`
- `私有同步到 GitHub`
- `准备发布`

v0.1 是规则驱动的本地 MVP，不依赖外部 API。

## 安装

```bash
pip install -e .
```

## 使用

```bash
project-copilot 检查项目
project-copilot 初始化项目
project-copilot 接管这个已有项目
project-copilot 继续开发项目
project-copilot 今天结束工作
project-copilot 检查 OSS 准备度
project-copilot 准备开源
project-copilot 私有同步到GitHub
```

也可以直接运行模块：

```bash
python -m project_copilot.cli.main 检查项目
```

## v0.1 能力

- 项目初始化：生成 `README.md`、`LICENSE`、`AGENTS.md`、`docs/` 和 `.ai/` 记忆文件。
- 已有项目接管：扫描现有文件，非破坏式生成 `.ai/` 项目记忆和接管报告。
- 项目记忆：维护 `PROJECT_CONTEXT.md`、`MEMORY.md`、`ROADMAP.md`、`STATUS.md`、`DECISIONS.md`、`WORKFLOW.md`、`USER_PROFILE.md`。
- 项目状态分析：检查 Git、基础文件、缺失项、风险和下一步建议。
- 开发会话管理：继续开发、结束工作、今日总结。
- OSS 检查：输出 OSS Readiness Score 和改进建议。
- 开源准备：生成贡献指南、安全策略、行为准则、变更日志、Issue 模板和 PR 模板。
- GitHub 同步：规划 public/private 仓库同步，检查 remote、GitHub CLI 和仓库地址。
- 自然语言意图：用中文或简单英文触发工作流。

## 调度架构

自然语言请求统一进入 `intent` 识别，输出标准 `intent_name`。`workflow` engine 根据 `intent_name` 注册和分发工作流；每个工作流单独一个文件，并在内部调用 `analyzer`、`planner`、`memory`、`oss`、`gitops` 等模块。CLI 只调用 workflow engine。

第一阶段核心工作流：

- `init_project`
- `check_project`
- `continue_development`
- `close_day`
- `oss_check`
- `prepare_oss`
- `github_sync`

## 目录结构

```text
project_copilot/
  analyzer/
  cli/
  gitops/
  intent/
  memory/
  oss/
  planner/
tests/
docs/
```
