# Agents

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

