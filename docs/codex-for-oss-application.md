# Codex for Open Source Application

## Project Name

Project Copilot

## Repository

https://github.com/Yingxing-AI/project-copilot

## One-Sentence Summary

Project Copilot is an AI-native engineering memory layer for Codex that helps long-running software projects preserve mission, scope, ADRs, session summaries, and derived validation from real project state.

## What Problem It Solves

Long-running projects often lose the reasoning behind their current structure. Git can show what changed, but it does not reliably preserve why the project exists, why decisions were made, what was intentionally excluded, or how product scope evolved.

Project Copilot solves that gap by giving Codex a persistent, local-first project memory surface built around:

- project charter
- ADRs
- session archive
- memory health
- derived validation

This helps Codex resume work with stronger context and helps maintainers keep project reasoning readable over time.

## Why It Is A Good Fit For Codex

Project Copilot is designed specifically around Codex-native collaboration:

- users talk to Codex, not to a separate project-management UI
- Project Copilot keeps memory local in Markdown under `.ai/`
- the workflows are deterministic and rule-driven
- the product avoids overlapping with Git, release orchestration, or code-editing responsibilities that Codex already covers well

The result is a narrow but useful support layer that improves continuity without competing with the coding agent itself.

## Current State

- Stable release: `v0.3.2`
- Python package with CLI entrypoint
- MIT licensed
- GitHub Actions CI across Python 3.10, 3.11, and 3.12
- Local install script for stable usage
- Real multi-project validation support
- OSS governance docs in place:
  - `CONTRIBUTING.md`
  - `CODE_OF_CONDUCT.md`
  - `SECURITY.md`

## Quality Signals

- Test suite: `65 passed`
- Coverage entry available in CI and locally with:

```bash
pytest -q --cov=project_copilot --cov-report=term-missing
```

- Current measured coverage is approximately 84%
- Validation includes:
  - README Drift Check
  - ADR Governance
  - Session Quality
  - Legacy Migration Report
  - Multi-Project Validation

## Why Support Would Help

Support from Codex for Open Source would help accelerate:

- broader dogfooding across real projects
- stronger contributor onboarding
- deeper validation of long-term memory workflows
- improved coverage in lower-tested review and timeline modules
- more public examples of Codex-native project maintenance patterns

## Why This Project Is Worth Supporting

Project Copilot is not trying to be a general AI platform or another developer tool suite. It is intentionally narrow: it gives Codex a persistent memory structure that stays local, reviewable, testable, and maintainable.

That focus makes it a good candidate for support:

- it is clearly scoped
- it is already usable
- it has a stable public release
- it has evidence of real usage and validation
- it extends Codex in a way that is complementary rather than redundant

## Additional Notes

- The project keeps legacy compatibility files for migration safety, but active workflows now prefer ADRs and session-based memory paths.
- The maintainers treat governance and validation as first-class product surfaces, not just documentation afterthoughts.
