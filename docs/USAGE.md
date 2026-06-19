# Usage

Project Copilot installs and maintains a layered project memory set for Codex.

用户只和 Codex 对话。Project Copilot 负责初始化 `.ai/` 项目记忆、生成 `AGENTS.md` 规则和 `docs/CODEX_WORKFLOW.md`，让 Codex 在日常开发中记住项目为什么这样做。

## Install

Recommended one-command install:

```bash
curl -LsSf https://raw.githubusercontent.com/Yingxing-AI/project-copilot/main/install.sh | sh
```

Developer install from a local checkout:

```bash
pip install -e .
```

## Primary Flow

Adopt an existing project:

```bash
project-copilot adopt
codex
```

Initialize a new project:

```bash
project-copilot init
codex
```

先贴完整项目方案。Project Copilot 会先提取关键字段，只有在信息缺失时才追问。

After this, work directly in Codex:

```text
继续开发这个项目
```

Project memory gives Codex the context it needs for later conversations, while keeping project context, ADR, session candidates, long-term knowledge, and derived validation data separate.

## Low-Frequency Tools

```bash
project-copilot init
project-copilot adopt
project-copilot doctor
```

Chinese aliases:

```bash
project-copilot 初始化项目
project-copilot 接管已有项目
project-copilot 检查秘书配置
```

## Generated Files

Project Copilot generates:

- `.ai/`
- `AGENTS.md`
- `docs/CODEX_WORKFLOW.md`

`.ai/` contains:

- `PROJECT_CONTEXT.md`
- `STATUS.md`
- `ROADMAP.md`
- `MEMORY.md`
- `HYPOTHESES.md`
- `DECISIONS.md`
- `adr/`
- `sessions/current.md`
- `sessions/archive/`
- `WORKLOG.md`
- `KNOWLEDGE.md`
- `metrics.md` 作为辅助快照，不作为事实源
- `history/`

## Codex Daily Use

每天开始：

```bash
codex
```

Then say:

```text
继续开发这个项目
```

每天结束时说：

```text
今天结束工作
```

This shows session candidates for confirmation. Ordinary code changes, tests, and small bug fixes stay in Git/Codex instead of long-term `.ai` memory.

每周复盘时说：

```text
复盘项目
```

Use this to review completed work, key decisions, risk changes, roadmap progress, and drift risk.

## Compatibility Commands

These commands remain available, but they are not the primary daily entry point:

```bash
project-copilot 项目状态
project-copilot 项目复盘
project-copilot 项目时间轴
project-copilot 项目偏航检查
project-copilot 记录决策 MVP 先做简历导入
project-copilot 查看路线图
project-copilot 继续开发项目
project-copilot 今天结束工作
```

Interactive mode is also kept for compatibility:

```bash
project-copilot
```

Prefer `project-copilot adopt` or `project-copilot init`, then `codex`.

## Verification

Run tests:

```bash
pytest -q
```

Validation reports are normally refreshed by memory-writing workflows. Manual refresh is only needed when repairing or re-generating derived reports:

```bash
project-copilot 刷新验证报告
```
