# Project Copilot Demo Script

This document contains two 30-second demo scripts for Project Copilot.

## Demo 1: Adopt Existing Project

Goal: show how Project Copilot can take over an existing codebase without overwriting user files.

### Setup

Start in an existing repository that already has code, docs, or tests.

### Script

Narration:

> "This is an existing project. Instead of manually documenting the project state, I can ask Project Copilot to adopt it."

Command:

```bash
project-copilot 接管这个已有项目
```

Narration:

> "Project Copilot scans the repository, detects project signals, and creates local `.ai` memory files without replacing my existing README, license, source code, or docs."

Command:

```bash
project-copilot 检查项目
```

Narration:

> "Now I get a project health summary, current risks, missing files, and next steps. The result is local, reviewable, and ready to commit."

Show:

- `.ai/PROJECT_CONTEXT.md`
- `.ai/STATUS.md`
- Project health output

Close:

> "Project Copilot turns an existing repository into an AI-coding-ready project workspace."

## Demo 2: New Project Lifecycle

Goal: show the basic lifecycle from initialization to development continuation and end-of-day memory update.

### Setup

Start in an empty project directory.

### Script

Narration:

> "For a new project, I can start with one natural-language command."

Command:

```bash
project-copilot 初始化项目
```

Narration:

> "Project Copilot creates the basic project files and `.ai` memory so future sessions have context."

Command:

```bash
project-copilot 继续开发项目
```

Narration:

> "When I come back later, Project Copilot reads the project memory and tells me the current phase and suggested next steps."

Command:

```bash
project-copilot 今天结束工作
```

Narration:

> "At the end of the day, it updates the project status, worklog, and memory so the next development session starts with the right context."

Show:

- `README.md`
- `.ai/STATUS.md`
- `.ai/MEMORY.md`
- `.ai/WORKLOG.md`

Close:

> "The full loop is natural language in, structured project memory out."
