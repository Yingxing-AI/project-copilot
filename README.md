# Project Copilot

Natural Language Operating System for AI Coding Projects.

Project Copilot 是一个面向 AI Coding 项目的自然语言项目操作系统。它把“检查项目”“继续开发”“今天结束工作”“准备开源”这类自然语言输入，转换成本地、可重复的项目工作流。

它解决的问题很直接：开发者不应该在每个项目里重复记忆 Git、Python、开源准备、项目状态和工作流命令。Project Copilot 用一个中文优先的 CLI，把这些项目操作组织成可持续维护的 workflow，并把项目上下文写入 `.ai/` 记忆目录。

当前版本是 v0.3.0a3：规则驱动、本地运行、不依赖外部 AI API。

## Available Today

- Natural-language intent recognition
- Workflow engine
- Interactive CLI mode
- Command mode
- `.ai/` project memory
- Project initialization
- Existing-project adoption
- Project health check
- Continue development workflow
- Close day workflow
- OSS readiness check
- OSS preparation workflow
- GitHub sync planning and preflight checks
- One-command GitHub push, tag, and release workflow with dry-run checks
- GitHub Actions CI for Python 3.10, 3.11, and 3.12
- Unknown intent suggestions
- Automatic project state sync for `.ai/STATUS.md`, Roadmap, Changelog, and the managed `AGENTS.md` block
- Pytest coverage for the current workflow surface

## Quick Start

Install from the repository in editable mode:

```bash
pip install -e .
```

Verify the installed CLI:

```bash
project-copilot --help
project-copilot --version
project-copilot doctor
```

Start interactive mode:

```bash
project-copilot
```

Run a single workflow:

```bash
project-copilot 检查项目
```

Sync project status, roadmap, changelog, and the managed `AGENTS.md` block:

```bash
project-copilot 同步项目状态
```

Create a release with push, tag, and GitHub Release:

```bash
project-copilot 发布 v0.3.0-alpha.3
```

Preview release actions without changing GitHub:

```bash
project-copilot 发布 v0.3.0-alpha.3 dry-run
```

Run without installing the console script:

```bash
python3 -m project_copilot.cli.main 检查项目
```

## Demo

![Demo](docs/demo/demo.svg)

Demo scripts:

- [Adopt Existing Project](docs/demo-script.md#demo-1-adopt-existing-project)
- [New Project Lifecycle](docs/demo-script.md#demo-2-new-project-lifecycle)

## Usage Examples

Initialize a project:

```bash
project-copilot 初始化项目
```

Adopt an existing project without overwriting existing files:

```bash
project-copilot 接管这个已有项目
```

Check project status:

```bash
project-copilot 检查项目
```

Continue from project memory:

```bash
project-copilot 继续开发项目
```

Close the day and update project memory:

```bash
project-copilot 今天结束工作
```

Check open-source readiness:

```bash
project-copilot 检查 OSS 准备度
```

Prepare open-source community files:

```bash
project-copilot 准备开源
```

Plan private GitHub sync:

```bash
project-copilot 私有同步到 GitHub
```

Publish a release:

```bash
project-copilot 发布 v0.3.0-alpha.3
```

Preview a release:

```bash
project-copilot 发布 v0.3.0-alpha.3 dry-run
```

Run against another project root:

```bash
project-copilot --root /path/to/project 检查项目
```

## Interactive Mode

Run `project-copilot` with no arguments to enter interactive mode.

The CLI shows a short project status summary, then accepts continuous natural-language input:

```text
Project Copilot 交互模式
项目状态摘要：
- 当前阶段：可持续开发
- 健康度：92/100
- Git：main
常用输入：检查项目、继续开发项目、今天结束工作、检查 OSS 准备度。
输入 exit / quit / 退出 结束。
project-copilot>
```

Exit commands:

- `exit`
- `quit`
- `退出`

If an intent cannot be recognized, Project Copilot returns a short list of available suggestions instead of running the wrong workflow.

## Command Mode

Command mode keeps the existing one-shot workflow style:

```bash
project-copilot 检查项目
project-copilot 初始化项目
project-copilot 接管这个已有项目
project-copilot 继续开发项目
project-copilot 今天结束工作
project-copilot 检查 OSS 准备度
project-copilot 准备开源
project-copilot 私有同步到 GitHub
```

## Architecture

![Project Copilot architecture](docs/architecture.svg)

The CLI does not call workflow modules directly. It sends user text to the workflow engine, which classifies the intent, dispatches to a registered workflow, and renders a `WorkflowResult`.

More details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Project Memory

Project Copilot stores project memory under `.ai/`.

Current memory files:

- `.ai/PROJECT_CONTEXT.md`: project identity, goals, users, stack, constraints
- `.ai/STATUS.md`: current phase, completed work, next steps
- `.ai/ROADMAP.md`: local roadmap used by development sessions
- `.ai/MEMORY.md`: chronological project events
- `.ai/DECISIONS.md`: project decisions and ADR-style notes
- `.ai/WORKFLOW.md`: workflow conventions
- `.ai/USER_PROFILE.md`: user preferences and collaboration defaults

The memory system is local Markdown. It is designed to be readable, reviewable, and commit-friendly.

## Coming Soon

- Better project analysis
- Stronger existing-project adoption reports
- Git history analysis
- Stronger release and changelog automation
- Optional AI Provider integrations
- Codex Skill packaging
- Codex Plugin packaging

## Development

Run tests:

```bash
pytest -q
```

Current baseline:

```text
30 passed
```

## Contributing

Contributions are welcome. Good first contributions include:

- Better intent examples
- More workflow tests
- Documentation improvements
- Project analysis improvements
- Existing-project adoption improvements

Before opening a pull request, run:

```bash
pytest -q
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/USAGE.md](docs/USAGE.md).

## License

MIT License. See [LICENSE](LICENSE).
