# Project Context

项目名称：Project Copilot

项目是什么：Codex 项目的项目记忆层。Codex 负责开发，Git 负责版本管理，Project Copilot 负责帮助 Codex 持续记住项目背景、MVP 边界、关键决策原因和长期知识。

项目目标：让非专业开发者不需要记忆工程术语，也能让 Codex 在长期开发中持续理解项目为什么做、为什么这样设计、哪些需求被放弃、项目如何演化。

目标用户：

- 创业者。
- 产品经理。
- 业务人员。
- AI Coding 新手。
- 使用 Codex 开发项目的非专业开发者。

技术栈：

- Python 3.10+
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
- ADR：`.ai/adr/`
- Session Memory：`.ai/sessions/`

当前约束：

- 当前版本不依赖外部 API。
- 默认非破坏式处理已有项目文件。
- Project Copilot 不与 Codex 竞争，不负责写代码、修 Bug 或替代技术方案设计。
- Project Copilot 不负责 commit、push、release、测试或代码修改 workflow。
- 开发过程中不自动扩写长期记忆；结束工作时统一确认 Session 候选事件。
- 需要保持根目录文档和 `.ai/` 项目记忆同步。
