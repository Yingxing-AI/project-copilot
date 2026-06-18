# Codex for Open Source Readiness

Project Copilot helps open-source maintainers use Codex without losing project context. It installs a local Project Memory Layer for Codex projects.

## Fit

- Installs a local `.ai/` project memory layer.
- Generates Codex rules in `AGENTS.md`.
- Keeps project mission, MVP scope, decisions, work logs, and lessons in versioned Markdown.
- Works without external API credentials.
- Keeps daily work in Codex instead of adding another chat surface.

## Value for Maintainers

- New contributors can understand why the project exists.
- Codex can read project memory before changing code.
- Maintainers can record decisions without creating a heavyweight process.
- Project drift can be caught before implementation.

## Safety and Trust

- Local-first by default.
- No background service.
- No external AI provider configuration.
- No dependency beyond Python packaging tools.
- Existing `AGENTS.md` content is preserved; Project Copilot appends a managed block.

## Current Evidence

- Tagged Beta release: `v0.3.0-beta.1`.
- CI runs on Python 3.10, 3.11, and 3.12.
- Current test baseline: `pytest -q` passes with 59 tests.
- Validation report: [validation-report.md](validation-report.md).
- Case studies: [case-studies/](case-studies/).

## Gaps Before Wider Outreach

- Add more real open-source project case studies.
- Turn validation evidence from one active project plus one queued project into a stronger cross-project sample set.
- Publish a PyPI package in addition to the GitHub install path.
- Keep release notes and installer tags in sync.
- Continue measuring work logs, decisions, and knowledge entries across projects.
