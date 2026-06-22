# Contributing

Thanks for your interest in Project Copilot.

## Development Setup

Requirements:

- Python 3.10+
- Git

Clone the repository and install development dependencies:

```bash
git clone https://github.com/Yingxing-AI/project-copilot.git
cd project-copilot
python3 -m pip install -e ".[dev]"
```

## Test And Verification

Run the main test suite:

```bash
pytest -q
```

Run coverage locally when changing workflows, validation, or contributor-facing behavior:

```bash
pytest -q --cov=project_copilot --cov-report=term-missing
```

Recommended quick checks before opening a PR:

```bash
project-copilot --version
project-copilot doctor
```

## Project Areas

- `project_copilot/cli/`: CLI entrypoints and doctor output
- `project_copilot/intent/`: natural-language intent classification
- `project_copilot/workflow/`: user-facing memory workflows
- `project_copilot/memory/`: `.ai` memory storage and memory health
- `project_copilot/validation/`: derived validation snapshots and reports

## Pull Requests

- Keep changes focused.
- Add or update tests for behavior changes.
- Update README or docs when user-facing behavior changes.
- Update `.ai/release/` notes when preparing a tagged release.
- Prefer small PRs that are easy to review.

## Issues

Please include the workflow you ran, the expected result, and the actual result.

## Release Notes

Stable releases currently follow the `v0.x.y` tag format and keep a matching note in `.ai/release/`.
