from __future__ import annotations

from pathlib import Path

from project_copilot.oss import check_oss_readiness
from project_copilot.workflow.types import WorkflowContext, WorkflowResult


FILES: dict[str, str] = {
    "LICENSE": """MIT License

Copyright (c) 2026 Project Copilot Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",
    "CONTRIBUTING.md": """# Contributing

Thanks for your interest in Project Copilot.

## Development

```bash
pytest -q
```

## Pull Requests

- Keep changes focused.
- Add or update tests for behavior changes.
- Update README or docs when user-facing behavior changes.
- Prefer small PRs that are easy to review.

## Issues

Please include the workflow you ran, the expected result, and the actual result.
""",
    "CODE_OF_CONDUCT.md": """# Code of Conduct

Project Copilot aims to be a respectful and practical open source community.

## Expected Behavior

- Be respectful and constructive.
- Focus feedback on the work.
- Help make the project easier to use and contribute to.

## Unacceptable Behavior

- Harassment, insults, or personal attacks.
- Publishing private information without permission.
- Repeated disruption of project discussions.

Maintainers may remove content or restrict participation when needed to protect the community.
""",
    "SECURITY.md": """# Security Policy

## Reporting a Vulnerability

Please do not open a public issue for sensitive security reports.

For now, report security concerns by opening a private advisory on GitHub if available, or by contacting the maintainers through the repository owner profile.

## Scope

Project Copilot v0.1 is a local CLI tool and does not require external API credentials.
""",
    "CHANGELOG.md": """# Changelog

## v0.1.0

- Added natural-language intent routing.
- Added workflow engine.
- Added project memory, status analysis, OSS readiness checks, and CLI entrypoint.
""",
    "RELEASE.md": """# Release Notes

## v0.1.0

Project Copilot v0.1 is a public beta for local natural-language project workflows.
""",
    ".github/pull_request_template.md": """## Summary

## Tests

## Notes
""",
    ".github/ISSUE_TEMPLATE/bug_report.yml": """name: Bug report
description: Report something that is broken
title: "[Bug]: "
labels: ["bug"]
body:
  - type: textarea
    id: description
    attributes:
      label: What happened?
      description: Describe the bug and what you expected.
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: Steps to reproduce
      description: Include commands or natural-language workflow input.
    validations:
      required: true
""",
    ".github/ISSUE_TEMPLATE/feature_request.yml": """name: Feature request
description: Suggest an improvement
title: "[Feature]: "
labels: ["enhancement"]
body:
  - type: textarea
    id: problem
    attributes:
      label: Problem
      description: What user problem should this solve?
    validations:
      required: true
  - type: textarea
    id: proposal
    attributes:
      label: Proposal
      description: Describe the workflow or behavior you want.
""",
    ".github/topics.yml": """topics:
  - ai-coding
  - codex
  - developer-tools
  - project-management
  - workflow-automation
  - python
  - cli
  - open-source
""",
}


def run(context: WorkflowContext) -> WorkflowResult:
    context.root.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    kept: list[str] = []

    for relative_path, content in FILES.items():
        path = context.root / relative_path
        if path.exists():
            kept.append(relative_path)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        created.append(relative_path)

    readiness = check_oss_readiness(context.root)
    return WorkflowResult(
        intent_name=context.intent_name,
        status="success",
        title="已完成开源准备文件检查。",
        summary=f"OSS Readiness Score：{readiness.score}/100",
        details={"创建文件": created, "保留已有文件": kept, "仍缺失": readiness.missing},
        next_steps=["确认 README、LICENSE 和仓库主题后创建公开仓库。"],
    )
