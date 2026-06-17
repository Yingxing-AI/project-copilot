# Project Context

项目名称：Project Copilot

项目是什么：Codex 项目的项目秘书。Codex 负责开发，Project Copilot 负责记录项目背景、关键决策、工作历史、路线图、复盘和偏航提醒。

项目目标：让非专业开发者不需要记忆工程术语，也能连续追踪一个 AI Coding 项目为什么做、为什么这样设计、哪些需求被放弃、项目如何演化。

目标用户：

- 创业者。
- 产品经理。
- 业务人员。
- AI Coding 新手。
- 使用 Codex 开发项目的非专业开发者。

技术栈：

- Python 3.11+
- setuptools packaging
- pytest
- 规则驱动 intent classifier
- 本地文件系统 `.ai/` 项目记忆

核心入口：

- CLI：`project_copilot/cli/main.py`
- Intent：`project_copilot/intent/classifier.py`
- Workflow engine：`project_copilot/workflow/engine.py`
- Project analyzer：`project_copilot/analyzer/project.py`
- Memory store：`project_copilot/memory/store.py`

当前约束：

- 当前版本不依赖外部 API。
- 默认非破坏式处理已有项目文件。
- Project Copilot 不与 Codex 竞争，不负责写代码、修 Bug 或替代技术方案设计。
- 需要保持根目录文档和 `.ai/` 项目记忆同步。
