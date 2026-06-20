# Project Copilot

AI Native Engineering Memory Layer for Codex.

Project Copilot helps Codex remember the project. It does not manage the project for Codex.

用户只和 Codex 对话。Codex 负责开发，Git 负责版本管理，Project Copilot 负责安装和维护 `.ai/` 项目记忆，让 Codex 持续理解项目使命、MVP 边界、ADR、长期知识和为什么这样做。

当前版本是 v0.3.0：规则驱动、本地运行、不依赖外部 AI API。

## Available Today

- Codex-native project memory installation
- `AGENTS.md` rules for Codex
- `docs/CODEX_WORKFLOW.md` user guide for working with Codex
- `PROJECT_CHARTER` for mission, MVP, target users, and boundaries
- `ADR` for long-lived engineering and product decisions
- `Session Archive` for confirmed major session summaries
- `Memory Health` for core memory-layer checks
- `Validation` derived from real `.ai` state
- Existing-project adoption
- New-project initialization
- Local doctor checks
- Natural-language intent recognition
- Project review
- Project timeline
- Drift check for MVP scope
- Decision recording
- Continue development context recovery
- Close-day Session Memory confirmation
- README Drift Check
- ADR Governance
- Session Quality
- Legacy Migration Report
- Multi-Project Validation
- Validation snapshots derived from real `.ai`
- Pytest coverage for the current memory surface

## Not Project Copilot's Job

These belong to Codex, Git, or the hosting platform:

- commit
- push
- tag
- release
- testing
- code modification
- GitHub sync
- OSS preparation workflow

## Quick Start

Install with one command:

```bash
curl -LsSf https://raw.githubusercontent.com/Yingxing-AI/project-copilot/main/install.sh | sh
```

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

Adopt an existing project:

```bash
project-copilot adopt
```

Or initialize a new project:

```bash
project-copilot init
```

Project Copilot generates:

- `.ai/`
- `AGENTS.md`
- `docs/CODEX_WORKFLOW.md`

Then work in Codex:

```bash
codex
```

Tell Codex:

```text
继续开发这个项目
```

## Session Memory

Project Copilot uses a read-once, write-once memory rhythm:

- Start work: read `.ai` and restore project context.
- During work: do not automatically expand Roadmap, Memory, or Worklog.
- During work: keep only session candidates such as ADR candidates, milestones, risks, and knowledge.
- End work: confirm what still matters three months from now.
- After confirmation: write accepted items to `.ai/adr/`, `.ai/MEMORY.md`, `.ai/KNOWLEDGE.md`, or `.ai/sessions/archive/`.

普通代码修改、测试增加、小型 Bug 修复和临时讨论由 Git/Codex 承载，不进入长期项目记忆。

## Core Memory Structure

`.ai/` stores the project memory:

- `PROJECT_CHARTER.md`: mission, target users, MVP scope, non-goals, boundaries
- `PROJECT_CONTEXT.md`: legacy project context compatibility
- `STATUS.md`: current recovery card
- `ROADMAP.md`: product direction and future memory work
- `MEMORY.md`: stable project timeline and milestones
- `HYPOTHESES.md`: legacy hypothesis layer
- `DECISIONS.md`: legacy decision index
- `adr/`: ADR files for long-lived decisions and tradeoffs
- `sessions/current.md`: current session candidates
- `sessions/archive/`: confirmed major session summaries
- `WORKLOG.md`: legacy worklog compatibility only
- `KNOWLEDGE.md`: long-term practices, product learning, and feedback
- `derived/metrics.json`: generated memory metrics
- `metrics.md`: legacy metrics snapshot, not created for new projects
- `validation.json`: validation data derived from `.ai`

## Primary Flow

```bash
project-copilot adopt
codex
```

or:

```bash
project-copilot init
codex
```

Daily natural-language examples:

```text
继续开发这个项目
项目现在怎么样
最近发生了什么
这个想法靠谱吗
今天结束工作
```

The user should not need to think in commands. Project Copilot maps intent to the right memory workflow internally.

## Validation

Project Copilot validates itself from real project `.ai` data. Users do not maintain a separate validation system.

Validation refresh policy:

- Long-term memory writes refresh validation automatically.
- Validation snapshot export refreshes the report automatically.
- Session candidates do not refresh validation until confirmed and written.
- Manual refresh remains available as a compatibility and repair command.

Available compatibility workflows:

```bash
project-copilot 导出验证快照
project-copilot 刷新验证报告
```

Validation focuses on whether project memory remains readable, maintainable, and useful after time passes.
It tracks memory quality signals such as Charter presence, ADR count, Session Archive count, active candidates, Roadmap presence, memory drift, README drift, ADR governance, session quality, and legacy migration progress.

## Governance

P2 adds rule-based memory governance to prove long-term value from real project usage:

- `README Drift Check`: detect README drift against Charter, ADR, Session Archive, Validation, and Memory Health
- `ADR Governance`: detect missing status, number conflicts, and broken superseded chains
- `Session Quality`: detect archives that are too short, too long, noisy, or duplicating ADR content
- `Legacy Migration Report`: classify old files as Active, Compatibility, Legacy, or Safe To Remove
- `Multi-Project Validation`: aggregate multiple projects from `validation/sources.yaml` without hand-maintained reports

## Compatibility

Interactive mode is kept for compatibility. It is not the primary daily workflow; prefer `project-copilot adopt` or `project-copilot init`, then use `codex`.

```bash
project-copilot
```

## Architecture

The CLI sends user text to the workflow engine, which classifies intent, dispatches to a registered memory workflow, and renders a `WorkflowResult`.

More details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
