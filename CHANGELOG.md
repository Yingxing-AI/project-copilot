# Changelog

## v0.3 Alpha

Project Copilot is now packaged as a local-first natural-language project workflow CLI for AI Coding projects.

### Changed

- Repositioned Project Copilot as the project secretary for Codex projects.
- Added question-based first-use onboarding that generates `PROJECT_CONTEXT.md`.
- Reworked startup and project check output into a secretary-style project status card.
- Softened user-facing wording for cloud backup and version publishing.

### Added

- Natural-language intent recognition.
- Workflow engine with registered project workflows.
- `.ai/` project memory files.
- Project initialization workflow.
- Existing-project adoption workflow.
- Project health check workflow.
- Continue development workflow.
- Close day workflow.
- OSS readiness check workflow.
- OSS preparation workflow.
- GitHub sync planning and preflight checks.
- Interactive CLI mode.
- Command mode.
- Unknown intent suggestions.
- README, roadmap, and OSS product documentation.
- `project-copilot --version`.
- `project-copilot doctor`.
- PEP 660 editable install with Hatchling.
- Demo scripts and README demo area.
- Architecture SVG and Mermaid source.
- Automatic project state sync for `.ai/STATUS.md`, Roadmap, and Changelog.
- Managed `AGENTS.md` synchronization block.
- One-command GitHub push, tag, and release workflow.
- GitHub Actions CI for Python 3.10, 3.11, and 3.12.
- Release dry-run and version/tag consistency checks.
- One-command install script for GitHub-based installation.
- Static promotional image for Project Copilot.
- Sprint Validation case study for real-project management with `ai-recruitment`.
- Project review workflow.
- Project timeline workflow.
- MVP drift check workflow.
- Decision recording workflow.
- Roadmap viewing workflow.
- `.ai/KNOWLEDGE.md`, `.ai/metrics.md`, and `.ai/history/`.

### Verified

- `pytest -q`
- Current baseline: 49 passed.

## v0.1.0

- Added natural-language intent routing.
- Added workflow engine.
- Added project memory, status analysis, OSS readiness checks, and CLI entrypoint.
