# Project Context

项目名称：Project Copilot

项目是什么：面向 AI Coding 场景的自然语言项目操作系统。用户用中文或简单英文表达项目意图，系统将其映射为本地工作流，完成初始化、接管、检查、继续开发、收工总结、OSS 准备和 GitHub 同步前置检查等任务。

项目目标：让用户不需要记忆 Git、Python、项目管理和开源运营命令，也能通过自然语言维护一个可持续开发的项目。

目标用户：

- 使用 AI Coding Agent 开发项目的个人开发者。
- 希望把项目初始化、状态检查、路线图和收工流程标准化的小团队。
- 想把已有项目非破坏式纳入 AI 项目记忆管理的开发者。

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

- v0.1 不依赖外部 API。
- 默认非破坏式处理已有项目文件。
- 需要保持根目录文档和 `.ai/` 项目记忆同步。
