from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REQUIRED_OSS_FILES = {
    "README": ("README.md",),
    "LICENSE": ("LICENSE",),
    "ROADMAP": ("ROADMAP.md", ".ai/ROADMAP.md"),
    "RELEASE": ("RELEASE.md",),
    "CHANGELOG": ("CHANGELOG.md",),
    "CONTRIBUTING": ("CONTRIBUTING.md",),
    "CODE_OF_CONDUCT": ("CODE_OF_CONDUCT.md",),
    "SECURITY": ("SECURITY.md",),
    "ISSUES": (".github/ISSUE_TEMPLATE",),
    "PULL_REQUEST_TEMPLATE": (".github/pull_request_template.md",),
    "TOPICS": (".github/topics.yml",),
}


@dataclass(frozen=True)
class OssReadiness:
    score: int
    present: list[str]
    missing: list[str]
    suggestions: list[str]


def check_oss_readiness(root: Path) -> OssReadiness:
    present = [label for label, paths in REQUIRED_OSS_FILES.items() if any((root / path).exists() for path in paths)]
    missing = [label for label, paths in REQUIRED_OSS_FILES.items() if not any((root / path).exists() for path in paths)]
    score = round(len(present) / len(REQUIRED_OSS_FILES) * 100)
    suggestions = [f"补充 {item}。" for item in missing]
    return OssReadiness(score, present, missing, suggestions)
