from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from project_copilot.memory.health import inspect_memory_health


ALLOWED_ADR_STATUSES = {"Proposed", "Accepted", "Superseded", "Deprecated"}
LEGACY_FILES = (
    "PROJECT_CONTEXT.md",
    "WORKLOG.md",
    "HYPOTHESES.md",
    "metrics.md",
    "DECISIONS.md",
)


@dataclass(frozen=True)
class ReadmeDriftReport:
    status: str
    issues: list[str]


@dataclass(frozen=True)
class AdrGovernanceReport:
    status: str
    issues: list[str]


@dataclass(frozen=True)
class SessionQualityReport:
    status: str
    issues: list[str]


@dataclass(frozen=True)
class LegacyMigrationReport:
    status: str
    progress: str
    classifications: dict[str, str]
    issues: list[str]


def inspect_readme_drift(root: Path) -> ReadmeDriftReport:
    readme_path = root / "README.md"
    if not readme_path.exists():
        return ReadmeDriftReport(status="缺少 README", issues=["README.md 缺失，无法验证文档是否与项目状态一致。"])

    readme = readme_path.read_text(encoding="utf-8")
    health = inspect_memory_health(root)
    issues: list[str] = []

    available_today = _section_lines(readme, "## Available Today")
    deprecated_mentions = {
        "Project status card": "README 仍把 `Project status card` 列为现有能力，但当前架构已收敛为 `Memory Health Summary`。",
    }
    for needle, issue in deprecated_mentions.items():
        if any(needle in line for line in available_today):
            issues.append(issue)

    required_capabilities = {
        "Memory Health": "README 缺少 Memory Health 能力说明，当前 `check_project` 已不再输出旧版项目健康卡。",
        "README Drift": "README 尚未说明 README Drift Check，无法反映 P2 的文档漂移治理能力。",
        "ADR Governance": "README 尚未说明 ADR Governance，无法反映 ADR 编号、状态和 superseded 链治理。",
        "Session Quality": "README 尚未说明 Session Quality，无法反映 Session Archive 的质量检查。",
        "Legacy Migration": "README 尚未说明 Legacy Migration Report，无法反映旧结构迁移进度。",
        "Multi-Project Validation": "README 尚未说明 Multi-Project Validation，无法反映跨项目统一统计能力。",
    }
    normalized = readme.lower()
    for label, issue in required_capabilities.items():
        if label.lower() not in normalized:
            issues.append(issue)

    if "Project status card" in readme and "Memory Health" not in readme:
        issues.append("README 对外仍沿用旧状态卡叙事，与 ADR 0006 的 Memory View 收敛决策冲突。")

    drift_days = _mtime_drift_days(
        readme_path,
        [
            root / ".ai" / "validation.json",
            root / ".ai" / "derived" / "metrics.json",
            *(root / ".ai" / "adr").glob("*.md"),
            *(root / ".ai" / "sessions" / "archive").rglob("*.md"),
        ],
    )
    if drift_days is not None and drift_days >= 1:
        issues.append(f"README 最后更新时间落后于 `.ai` 核心记忆与 validation 派生数据约 {drift_days} 天。")

    if health.status == "需要收敛记忆漂移" and "memory drift" not in normalized:
        issues.append("README 未解释当前记忆漂移治理面，难以说明 validation 与 memory health 的真实用途。")

    status = "已对齐" if not issues else "存在漂移"
    return ReadmeDriftReport(status=status, issues=issues)


def inspect_adr_governance(root: Path) -> AdrGovernanceReport:
    adr_dir = root / ".ai" / "adr"
    issues: list[str] = []
    number_to_path: dict[str, Path] = {}
    path_to_status: dict[Path, str] = {}
    superseded_targets: list[tuple[Path, str]] = []

    if not adr_dir.exists():
        return AdrGovernanceReport(status="缺少 ADR", issues=[".ai/adr/ 不存在，无法执行 ADR 治理检查。"])

    for path in sorted(adr_dir.glob("*.md")):
        if path.name == "index.md":
            continue
        number = _adr_number_from_name(path.name)
        text = path.read_text(encoding="utf-8")
        if not number:
            issues.append(f"{path.name} 未使用 `NNNN-title.md` 命名，ADR 编号不可治理。")
            continue
        if number in number_to_path:
            issues.append(f"ADR 编号冲突：`{number}` 同时出现在 `{number_to_path[number].name}` 和 `{path.name}`。")
        number_to_path[number] = path

        status = _extract_field(text, "状态")
        if not status:
            issues.append(f"{path.name} 缺少 `状态：` 字段。")
        elif status not in ALLOWED_ADR_STATUSES:
            issues.append(f"{path.name} 使用了无效状态 `{status}`；允许值为 {', '.join(sorted(ALLOWED_ADR_STATUSES))}。")
        else:
            path_to_status[path] = status

        superseded_by = _extract_field(text, "Superseded By")
        if superseded_by:
            superseded_targets.append((path, superseded_by))
        if status == "Superseded" and not superseded_by:
            issues.append(f"{path.name} 状态为 `Superseded`，但缺少 `Superseded By:`。")
        if status and status != "Superseded" and superseded_by:
            issues.append(f"{path.name} 存在 `Superseded By:`，但状态不是 `Superseded`。")

    for path, raw_target in superseded_targets:
        target_number = _adr_number_from_ref(raw_target)
        if not target_number:
            issues.append(f"{path.name} 的 `Superseded By:` 值 `{raw_target}` 不是有效 ADR 引用。")
            continue
        target_path = number_to_path.get(target_number)
        if target_path is None:
            issues.append(f"{path.name} 的 `Superseded By:` 指向 `{raw_target}`，但对应 ADR 不存在。")
            continue
        if target_path == path:
            issues.append(f"{path.name} 的 `Superseded By:` 不能指向自己。")

    status = "治理健康" if not issues else "需要治理"
    return AdrGovernanceReport(status=status, issues=issues)


def inspect_session_quality(root: Path) -> SessionQualityReport:
    archive_dir = root / ".ai" / "sessions" / "archive"
    issues: list[str] = []
    if not archive_dir.exists():
        return SessionQualityReport(status="缺少 Archive", issues=[".ai/sessions/archive/ 不存在，无法检查 Session Archive 质量。"])

    for path in sorted(archive_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        informative_bullets = [
            line.strip() for line in text.splitlines() if line.strip().startswith("- ") and "暂无" not in line and "说明：" not in line
        ]
        nonempty_lines = [line.strip() for line in text.splitlines() if line.strip()]
        generic_bullets = [line for line in informative_bullets if _is_noise_line(line)]
        if len(nonempty_lines) > 120 or len(informative_bullets) > 30:
            issues.append(f"{path.name} 偏长，建议压缩为重大会话摘要而不是完整流水。")
        if len(informative_bullets) < 2:
            issues.append(f"{path.name} 信息过少，未形成可复盘的重大会话摘要。")
        if _looks_like_copied_adr(text):
            issues.append(f"{path.name} 疑似重复 ADR 正文，应只保留会话级摘要和结论。")
        if informative_bullets and len(generic_bullets) / len(informative_bullets) >= 0.6:
            issues.append(f"{path.name} 噪音占比过高，维护动作多于长期重要结论。")
        if not informative_bullets and "暂无" in text:
            issues.append(f"{path.name} 基本仍是占位归档，尚未证明 Session Archive 的长期价值。")

    status = "质量健康" if not issues else "需要治理"
    return SessionQualityReport(status=status, issues=issues)


def inspect_legacy_migration(root: Path) -> LegacyMigrationReport:
    ai_dir = root / ".ai"
    health = inspect_memory_health(root)
    classifications: dict[str, str] = {}
    issues: list[str] = []

    context_path = ai_dir / "PROJECT_CONTEXT.md"
    worklog_path = ai_dir / "WORKLOG.md"
    hypotheses_path = ai_dir / "HYPOTHESES.md"
    metrics_path = ai_dir / "metrics.md"
    decisions_path = ai_dir / "DECISIONS.md"
    derived_metrics_path = ai_dir / "derived" / "metrics.json"

    classifications["PROJECT_CONTEXT.md"] = "Compatibility" if (ai_dir / "PROJECT_CHARTER.md").exists() else "Active"
    classifications["DECISIONS.md"] = "Compatibility" if health.adr_count > 0 else "Active"
    classifications["WORKLOG.md"] = "Legacy" if _has_active_worklog(worklog_path) else ("Compatibility" if worklog_path.exists() else "Safe To Remove")
    classifications["HYPOTHESES.md"] = "Legacy" if _has_active_hypotheses(hypotheses_path) else ("Compatibility" if hypotheses_path.exists() else "Safe To Remove")
    classifications["metrics.md"] = "Compatibility" if metrics_path.exists() and derived_metrics_path.exists() else ("Legacy" if metrics_path.exists() else "Safe To Remove")

    if classifications["WORKLOG.md"] == "Legacy":
        issues.append("WORKLOG.md 仍承载大量历史流水，尚未收敛为纯兼容层。")
    if classifications["HYPOTHESES.md"] == "Legacy":
        issues.append("HYPOTHESES.md 仍保留活跃内容，未完全迁移到 Session 候选。")
    if classifications["PROJECT_CONTEXT.md"] == "Compatibility":
        issues.append("PROJECT_CONTEXT.md 已被 Charter 取代，但仍需保留兼容读取与初始化写入。")
    if classifications["DECISIONS.md"] == "Compatibility":
        issues.append("DECISIONS.md 仍作为兼容索引存在，新决策已迁移到 ADR-first。")
    if classifications["metrics.md"] == "Compatibility":
        issues.append("metrics.md 仍保留兼容快照角色，真实指标已迁移到 derived/metrics.json。")

    counts = {
        "Active": sum(1 for value in classifications.values() if value == "Active"),
        "Compatibility": sum(1 for value in classifications.values() if value == "Compatibility"),
        "Legacy": sum(1 for value in classifications.values() if value == "Legacy"),
        "Safe To Remove": sum(1 for value in classifications.values() if value == "Safe To Remove"),
    }
    progress = (
        f"Active {counts['Active']} / Compatibility {counts['Compatibility']} / "
        f"Legacy {counts['Legacy']} / Safe To Remove {counts['Safe To Remove']}"
    )
    if counts["Legacy"] > 0:
        status = "迁移未完成"
    elif counts["Compatibility"] > 0:
        status = "迁移收敛中"
    else:
        status = "迁移完成"

    return LegacyMigrationReport(status=status, progress=progress, classifications=classifications, issues=issues)


def load_validation_project_roots(root: Path) -> list[Path]:
    config_path = root / "validation" / "sources.yaml"
    if not config_path.exists():
        return _default_validation_project_roots(root)

    configured_names = _parse_project_list(config_path.read_text(encoding="utf-8"))
    if not configured_names:
        return _default_validation_project_roots(root)

    roots: list[Path] = []
    seen: set[Path] = set()
    for name in configured_names:
        if name == root.name:
            candidate = root
        else:
            candidate = (root.parent / name).resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        roots.append(candidate)
    return roots


def _default_validation_project_roots(root: Path) -> list[Path]:
    candidates: list[Path] = [root]
    parent = root.parent
    if parent.exists():
        for candidate in parent.iterdir():
            try:
                if not candidate.is_dir():
                    continue
                candidates.append(candidate)
            except OSError:
                continue
    deduped: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        deduped.append(resolved)
    return deduped


def _parse_project_list(text: str) -> list[str]:
    in_projects = False
    projects: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line == "projects:":
            in_projects = True
            continue
        if not in_projects:
            continue
        if line.startswith("- "):
            projects.append(line[2:].strip())
        elif re.match(r"^[A-Za-z_]", line):
            break
    return [item for item in projects if item]


def _section_lines(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    collected: list[str] = []
    in_section = False
    for line in lines:
        if line.strip() == heading:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            collected.append(line)
    return collected


def _mtime_drift_days(reference: Path, candidates: list[Path]) -> int | None:
    try:
        reference_mtime = reference.stat().st_mtime
    except OSError:
        return None
    newer = []
    for candidate in candidates:
        try:
            if candidate.exists():
                newer.append(candidate.stat().st_mtime)
        except OSError:
            continue
    if not newer:
        return None
    newest = max(newer)
    if newest <= reference_mtime:
        return 0
    return int((newest - reference_mtime) // 86400) or 1


def _extract_field(text: str, field_name: str) -> str:
    match = re.search(rf"^{re.escape(field_name)}：(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _adr_number_from_name(name: str) -> str | None:
    match = re.match(r"^(\d{4})-", name)
    return match.group(1) if match else None


def _adr_number_from_ref(value: str) -> str | None:
    match = re.search(r"(\d{4})", value)
    return match.group(1) if match else None


def _looks_like_copied_adr(text: str) -> bool:
    if "# ADR " in text:
        return True
    matched_fields = sum(1 for label in ("背景：", "决策：", "原因：", "取舍：", "影响：") if label in text)
    return matched_fields >= 3


def _is_noise_line(line: str) -> bool:
    return any(
        token in line
        for token in (
            "已更新项目状态",
            "运行测试",
            "刷新验证",
            "同步",
            "修改文档",
            "修正文案",
            "补充测试",
        )
    )


def _has_active_worklog(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return bool(re.search(r"^##\s+\d{4}-\d{2}-\d{2}|^- 完成内容：|^- 已", text, flags=re.MULTILINE))


def _has_active_hypotheses(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return any(
        line.strip().startswith("- ") and "暂无" not in line and "说明：" not in line
        for line in text.splitlines()
    )
