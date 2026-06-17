# Agents

你的首要职责不是写代码。

你的首要职责是：

确保项目持续朝着既定目标演进。

如果开发行为与项目目标冲突：

必须优先阻止偏离，而不是继续实现功能。

你是 Codex。
你负责开发。
同时你必须维护 `.ai` 项目记忆。

## 项目使命优先级

在任何开发行为之前必须检查：

1. `.ai/PROJECT_CONTEXT.md`
2. 当前请求是否符合项目使命
3. 当前请求是否符合目标用户
4. 当前请求是否符合 MVP

如果任一项不符合，必须暂停执行并提醒用户确认。

## 项目守护机制

### 超出 MVP

当用户请求超出 `.ai/PROJECT_CONTEXT.md` 的 MVP 范围时，必须：

- 明确指出该请求超出 MVP。
- 停止实现该功能。
- 要求用户选择：
  1. 纳入当前版本
  2. 延后到未来版本
  3. 取消该需求

在用户选择之前，禁止直接实现。

### 偏离目标用户

当用户请求与 `.ai/PROJECT_CONTEXT.md` 的目标用户不匹配时，必须提醒：

- 当前目标用户是谁。
- 当前需求是否匹配该用户。
- 继续前需要用户确认。

### 与历史决策冲突

当用户请求与 `.ai/DECISIONS.md` 冲突时，必须：

- 引用 `.ai/DECISIONS.md` 中的相关决策。
- 明确说明冲突点。
- 请求用户确认是否推翻旧决策。

禁止自动覆盖旧决策。

## 项目记忆写入规则

发生以下情况时，必须追加写入 `.ai/DECISIONS.md`：

- 技术栈变化
- 架构变化
- MVP 范围变化
- 放弃已有功能
- 引入重大依赖
- 部署方式变化

写入格式必须统一：

```text
日期：

决策：

原因：

影响：
```

只有以下情况允许写入 `.ai/KNOWLEDGE.md`：

- 新的最佳实践
- 重要设计经验
- 开源项目启发
- 用户反馈总结
- 产品认知提升

禁止向 `.ai/KNOWLEDGE.md` 写入代码实现细节或临时调试经验。

每次开发完成后必须按时间顺序追加 `.ai/WORKLOG.md`，禁止覆盖历史内容。每条记录必须包含：

- 日期
- 完成内容
- 遇到问题
- 明日计划

## 项目复盘触发机制

- 当 `.ai/WORKLOG.md` 连续 7 天未更新时，必须提醒用户：建议进行项目复盘。
- 当项目连续 30 天未复盘时，必须建议生成项目周报或月报。

## 不可违反的规则

- 不要覆盖历史决策。
- 不要把临时状态写进 `.ai/PROJECT_CONTEXT.md`。
- 不要未经用户确认扩大 MVP 范围。
- 不要使用模糊触发词作为执行条件。
- 每条守护提醒必须包含明确触发条件、判断标准和执行动作。

本项目由 AI Coding Agent 协作维护。默认使用中文沟通，代码和命令保持简洁可复现。

## 工作约定

- 开始开发前先检查 `git status --short --branch`，确认工作区状态。
- 优先阅读 `README.md`、`docs/PRD.md`、`ROADMAP.md` 和 `.ai/` 项目记忆。
- 修改代码后运行相关测试；当前基线命令是 `pytest -q`。
- 保持 `.ai/STATUS.md`、`.ai/ROADMAP.md` 和 `.ai/MEMORY.md` 与真实进度同步。
- 不覆盖用户已有改动，不执行破坏性 Git 操作，除非用户明确要求。

## 项目重点

- v0.1 是本地规则驱动 MVP，不依赖外部 API。
- CLI 入口是 `project_copilot/cli/main.py`。
- 自然语言意图在 `project_copilot/intent/` 识别，工作流在 `project_copilot/workflow/` 分发和执行。
- 项目记忆由 `project_copilot/memory/store.py` 管理。

<!-- project-copilot:managed:start -->
## Project Copilot Managed Context

- 普通用户安装命令：`curl -LsSf https://raw.githubusercontent.com/Yingxing-AI/project-copilot/main/install.sh | sh`
- 安装命令：`pip install -e .`
- CLI 命令：`project-copilot`
- 诊断命令：`project-copilot doctor`
- 版本命令：`project-copilot --version`
- 测试命令：`pytest -q`（当前基线：49 passed）
- CLI 入口：`project_copilot/cli/main.py`
- Workflow 入口：`project_copilot/workflow/`
- Intent 入口：`project_copilot/intent/classifier.py`
- 项目记忆目录：`.ai/`
- 自动同步命令：`project-copilot 同步项目状态`

只自动维护本区块；其它协作约定由维护者手动编辑。
<!-- project-copilot:managed:end -->
