# Usage

Project Copilot can run as an installed console script or directly as a Python module.

## Install

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
