# Project Copilot

The Project Secretary for Codex Projects.

Project Copilot 是 Codex 项目的项目秘书。Codex 负责开发，Project Copilot 负责记住：项目背景、关键决策、工作历史、路线图、复盘和偏航提醒。

它面向创业者、产品经理、业务人员、AI Coding 新手和非专业开发者。用户不需要记工程术语，只需要用中文告诉 Project Copilot 要查看项目状态、记录决策、做项目复盘或检查是否跑偏。

当前版本是 v0.3.0a6：规则驱动、本地运行、不依赖外部 AI API。

## Alpha Notice

Project Copilot is currently an Alpha release. It is suitable for trial use, project workflow experiments, and developer feedback. Use it carefully for production or business-critical workflows.

## Available Today

- Natural-language intent recognition
- Workflow engine
- Interactive CLI mode
- Command mode
- `.ai/` project memory
- Question-based project onboarding
- Existing-project adoption
- Project status card
- Project review
- Project timeline
- Drift check for MVP scope
- Decision recording
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

Install with one command:

```bash
curl -LsSf https://raw.githubusercontent.com/Yingxing-AI/project-copilot/main/install.sh | sh
```

This installer is for macOS, Linux, and WSL. Native Windows PowerShell installation will be added later. See [Windows Install Notes](docs/INSTALL_WINDOWS.md).

Verify the installed CLI:

```bash
project-copilot --help
project-copilot --version
project-copilot doctor
```

For development, install from a local checkout:

```bash
pip install -e .
```

Start interactive mode:

```bash
project-copilot
```

Run a single workflow:

```bash
project-copilot 项目状态
```

Sync project status, roadmap, changelog, and the managed `AGENTS.md` block:

```bash
project-copilot 同步项目状态
```

Create a release with push, tag, and GitHub Release:

```bash
project-copilot 发布版本 v0.3.0-alpha.6
```

Preview release actions without changing GitHub:

```bash
project-copilot 发布版本 v0.3.0-alpha.6 dry-run
```

Run without installing the console script:

```bash
python3 -m project_copilot.cli.main 检查项目
```

## Demo

![Demo](docs/demo/demo.svg)

Promotional image:

![Project Copilot promotional image](docs/promo/project-copilot-promo.png)

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
project-copilot 项目状态
```

Review the project:

```bash
project-copilot 项目复盘
```

Show the project timeline:

```bash
project-copilot 项目时间轴
```

Check whether a new idea is outside the MVP:

```bash
project-copilot 项目偏航检查 新增商城模块
```

Record an important decision:

```bash
project-copilot 记录决策 MVP 先做简历导入
```

Show the roadmap:

```bash
project-copilot 查看路线图
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
project-copilot 备份到云端
```

Publish a release:

```bash
project-copilot 发布版本 v0.3.0-alpha.6
```

Preview a release:

```bash
project-copilot 发布版本 v0.3.0-alpha.6 dry-run
```

Run against another project root:

```bash
project-copilot --root /path/to/project 项目状态
```

## Interactive Mode

Run `project-copilot` with no arguments to enter interactive mode.

The CLI shows a secretary-style project status card, then accepts continuous natural-language input:

```text
欢迎使用 Project Copilot。
我是你的项目秘书。
项目状态卡片

项目：project-copilot
当前阶段：可持续开发
项目健康度：92
距离上次复盘：今天
路线图更新：今天

提醒：
- 暂无需要立即处理的提醒。
常用输入：项目状态、项目复盘、项目时间轴、项目偏航检查、记录决策、结束工作。
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
project-copilot 项目状态
project-copilot 初始化项目
project-copilot 接管这个已有项目
project-copilot 项目复盘
project-copilot 项目时间轴
project-copilot 项目偏航检查 新增商城模块
project-copilot 记录决策 MVP 先做简历导入
project-copilot 查看路线图
project-copilot 继续开发项目
project-copilot 今天结束工作
project-copilot 备份到云端
```

## Architecture

![Project Copilot architecture](docs/architecture.svg)

The CLI does not call workflow modules directly. It sends user text to the workflow engine, which classifies the intent, dispatches to a registered workflow, and renders a `WorkflowResult`.

More details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Project Memory

Project Copilot stores project memory under `.ai/`.

Current memory files:

- `.ai/PROJECT_CONTEXT.md`: 项目是什么、给谁用、MVP 是什么
- `.ai/STATUS.md`: 当前阶段、健康度、风险和提醒
- `.ai/ROADMAP.md`: 当前路线图和阶段目标
- `.ai/MEMORY.md`: 可读的项目历史
- `.ai/DECISIONS.md`: 关键决策、原因和影响
- `.ai/WORKLOG.md`: 每日工作记录
- `.ai/KNOWLEDGE.md`: 最佳实践、参考项目、产品认知、社区反馈和重要经验
- `.ai/metrics.md`: 健康度、复盘间隔、路线图更新时间等指标
- `.ai/history/`: 复盘和历史归档

The memory system is local Markdown. It is designed to be readable, reviewable, and easy to save with the project.

## Coming Soon

- Better project analysis
- Stronger existing-project adoption reports
- Better secretary reminders
- Softer wording for cloud backup and version publishing
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
32 passed
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
