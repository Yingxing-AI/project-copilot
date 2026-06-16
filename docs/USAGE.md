# Usage

Project Copilot can run as an installed console script or directly as a Python module.

## Install

Recommended one-command install:

```bash
curl -LsSf https://raw.githubusercontent.com/Yingxing-AI/project-copilot/main/install.sh | sh
```

This installs the latest published Project Copilot Alpha from GitHub. If `pipx` is available, the installer uses it. Otherwise it falls back to a user-level `pip` install.

This installer is for macOS, Linux, and WSL. Native Windows PowerShell installation will be added later. See [Windows Install Notes](INSTALL_WINDOWS.md).

Developer install from a local checkout:

```bash
pip install -e .
```

## Interactive Mode

Start the Chinese interactive CLI:

```bash
project-copilot
```

The prompt accepts continuous natural-language input.

Exit with:

```text
exit
quit
退出
```

## Command Mode

Show help:

```bash
project-copilot --help
```

Show version:

```bash
project-copilot --version
```

Check local environment:

```bash
project-copilot doctor
```

Sync project status, roadmap, changelog, and the managed `AGENTS.md` block:

```bash
project-copilot 同步项目状态
```

Create a GitHub release after push and tag:

```bash
project-copilot 发布 v0.3.0-alpha.3
```

Preview release actions without pushing, tagging, or creating a GitHub Release:

```bash
project-copilot 发布 v0.3.0-alpha.3 dry-run
```

Initialize a project:

```bash
project-copilot 初始化项目
```

Adopt an existing project:

```bash
project-copilot 接管这个已有项目
```

Check project status:

```bash
project-copilot 检查项目
```

Continue development:

```bash
project-copilot 继续开发项目
```

Close the day:

```bash
project-copilot 今天结束工作
```

Check OSS readiness:

```bash
project-copilot 检查 OSS 准备度
```

Prepare open-source files:

```bash
project-copilot 准备开源
```

Plan private GitHub sync:

```bash
project-copilot 私有同步到 GitHub
```

Run against another project root:

```bash
project-copilot --root /path/to/project 检查项目
```

Run as a Python module:

```bash
python3 -m project_copilot.cli.main 检查项目
```

## Common Workflow

```bash
project-copilot 检查项目
project-copilot 继续开发项目
project-copilot 今天结束工作
```

## Verification

Run tests:

```bash
pytest -q
```
