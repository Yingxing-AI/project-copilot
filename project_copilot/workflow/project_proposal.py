from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime


FIELD_LABELS: dict[str, tuple[str, ...]] = {
    "mission": ("项目使命", "项目是什么", "这个项目是做什么的", "项目简介", "项目目标"),
    "target_users": ("目标用户", "主要给谁使用", "面向谁", "用户群体", "受众"),
    "business_goal": ("商业目标", "业务目标", "商业价值", "变现目标", "产品目标"),
    "mvp_scope": ("MVP范围", "MVP 范围", "最小可交付版本", "最小可行产品", "第一版范围", "首版范围"),
    "tech_stack": ("技术栈", "技术方案", "技术选型", "实现技术"),
    "current_stage": ("当前阶段", "阶段", "当前进度", "项目阶段"),
    "roadmap": ("初始Roadmap", "初始 Roadmap", "Roadmap", "路线图", "计划", "里程碑"),
    "decisions": ("初始Decisions", "初始 Decisions", "Decisions", "决策", "关键决策", "设计决策"),
}
ALL_LABELS: tuple[str, ...] = tuple(
    dict.fromkeys(label for labels in FIELD_LABELS.values() for label in labels)
)


@dataclass(frozen=True)
class ProjectProposal:
    project_name: str
    mission: str = ""
    target_users: str = ""
    business_goal: str = ""
    mvp_scope: str = ""
    tech_stack: str = ""
    current_stage: str = ""
    roadmap_items: tuple[str, ...] = ()
    decision_items: tuple[str, ...] = ()
    missing_fields: tuple[str, ...] = ()
    source_text: str = ""


def parse_project_proposal(text: str, project_name: str) -> ProjectProposal:
    normalized_text = _normalize_text(text)
    sections = _collect_sections(normalized_text)
    mission = _pick_single_value(sections, "mission", normalized_text)
    target_users = _pick_single_value(sections, "target_users", normalized_text)
    business_goal = _pick_single_value(sections, "business_goal", normalized_text)
    mvp_scope = _pick_single_value(sections, "mvp_scope", normalized_text)
    tech_stack = _pick_single_value(sections, "tech_stack", normalized_text)
    current_stage = _pick_single_value(sections, "current_stage", normalized_text)
    roadmap_items = _pick_list_values(sections, "roadmap")
    decision_items = _pick_list_values(sections, "decisions")
    missing_fields = tuple(
        label
        for label, value in (
            ("项目使命", mission),
            ("目标用户", target_users),
            ("商业目标", business_goal),
            ("MVP 范围", mvp_scope),
            ("技术栈", tech_stack),
            ("当前阶段", current_stage),
            ("初始 Roadmap", "；".join(roadmap_items)),
            ("初始 Decisions", "；".join(decision_items)),
        )
        if not value.strip()
    )
    return ProjectProposal(
        project_name=project_name,
        mission=mission,
        target_users=target_users,
        business_goal=business_goal,
        mvp_scope=mvp_scope,
        tech_stack=tech_stack,
        current_stage=current_stage,
        roadmap_items=roadmap_items,
        decision_items=decision_items,
        missing_fields=missing_fields,
        source_text=normalized_text,
    )


def project_proposal_prompt(missing_fields: tuple[str, ...]) -> str:
    if not missing_fields:
        return ""
    fields = "、".join(missing_fields)
    return f"还缺少这些关键信息：{fields}。请直接补充，继续贴在上一段方案后面即可，不需要按问卷逐条回答。"


def build_project_context(project_name: str, proposal: ProjectProposal) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    return "\n".join(
        [
            "# Project Context",
            "",
            f"项目名称：{project_name}",
            "",
            f"项目使命：{_or_placeholder(proposal.mission)}",
            "",
            f"目标用户：{_or_placeholder(proposal.target_users)}",
            "",
            f"商业目标：{_or_placeholder(proposal.business_goal)}",
            "",
            f"MVP 范围：{_or_placeholder(proposal.mvp_scope)}",
            "",
            f"技术栈：{_or_placeholder(proposal.tech_stack)}",
            "",
            "说明：这里记录长期稳定背景，极少修改；不要写临时状态。",
            "",
            f"创建日期：{today}",
            "",
        ]
    )


def build_project_charter(project_name: str, proposal: ProjectProposal) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    return "\n".join(
        [
            "# Project Charter",
            "",
            f"项目名称：{project_name}",
            "",
            f"项目使命：{_or_placeholder(proposal.mission)}",
            "",
            f"目标用户：{_or_placeholder(proposal.target_users)}",
            "",
            f"商业目标：{_or_placeholder(proposal.business_goal)}",
            "",
            f"MVP 范围：{_or_placeholder(proposal.mvp_scope)}",
            "",
            "非目标：待确认。",
            "",
            f"技术栈：{_or_placeholder(proposal.tech_stack)}",
            "",
            "说明：这里记录长期稳定边界，极少修改；不要写临时状态。",
            "",
            f"创建日期：{today}",
            "",
        ]
    )


def build_status(project_name: str, proposal: ProjectProposal) -> str:
    focus = proposal.mvp_scope or "完善项目方案"
    risks = _compact_risk_list(proposal.missing_fields)
    next_steps = proposal.roadmap_items[:3] if proposal.roadmap_items else ("把初始方案拆成可执行任务",)
    lines = [
        "# Status",
        "",
        f"项目名称：{project_name}",
        "",
        f"当前阶段：{proposal.current_stage or '方案确认中'}",
        "",
        "当前重点：",
        f"- {focus}",
        "",
        "当前目标：",
        f"- {proposal.mission or '明确项目使命'}",
        "",
        "当前风险：",
    ]
    if risks:
        lines.extend(f"- {risk}" for risk in risks)
    else:
        lines.append("- 暂无。")
    lines.extend(["", "下一步任务："])
    lines.extend(f"- {step}" for step in next_steps)
    lines.append("")
    return "\n".join(lines)


def build_roadmap(proposal: ProjectProposal) -> str:
    backlog_items = list(proposal.roadmap_items) or ["待补充初始 Roadmap。"]
    in_progress: list[str] = []
    if proposal.current_stage and any(keyword in proposal.current_stage for keyword in ("进行", "推进", "开发", "落地", "实施")):
        in_progress = backlog_items[:1]
        backlog_items = backlog_items[1:]
    lines = ["# Roadmap", "", "## Backlog"]
    if backlog_items:
        lines.extend(f"- [ ] {item}" for item in backlog_items)
    else:
        lines.append("- [ ] 暂无。")
    lines.extend(["", "## In Progress"])
    if in_progress:
        lines.extend(f"- [ ] {item}" for item in in_progress)
    else:
        lines.append("暂无。")
    lines.extend(["", "## Done", "暂无。", ""])
    return "\n".join(lines)


def build_decisions(proposal: ProjectProposal) -> str:
    decision_items = list(proposal.decision_items) or ["待补充初始 Decisions。"]
    today = datetime.now().strftime("%Y-%m-%d")
    entries: list[str] = ["# Decisions", ""]
    for item in decision_items:
        decision, reason, impact = _split_decision(item)
        entries.extend(
            [
                f"## {today}",
                "",
                f"- 决策：{decision}",
                f"- 原因：{reason}",
                f"- 影响：{impact}",
                "",
            ]
        )
    return "\n".join(entries)


def _normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").strip()
    for label in ALL_LABELS:
        normalized = re.sub(rf"(?<=[^\s])\s*{re.escape(label)}\s*[：:]", f"\n{label}：", normalized)
    return normalized


def _collect_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_key, current_lines
        if current_key is None:
            return
        content = "\n".join(line.rstrip() for line in current_lines).strip()
        if content and current_key not in sections:
            sections[current_key] = content
        current_key = None
        current_lines = []

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            if current_key is not None and current_lines and current_lines[-1] != "":
                current_lines.append("")
            continue

        heading_match = re.match(r"^#{1,6}\s*(.+?)\s*$", stripped)
        if heading_match:
            flush()
            current_key = heading_match.group(1).strip()
            current_lines = []
            continue

        labeled_match = re.match(r"^([A-Za-z\u4e00-\u9fff][^:：]{0,40}?)\s*[：:]\s*(.*)$", stripped)
        if labeled_match:
            flush()
            current_key = labeled_match.group(1).strip()
            current_lines = []
            inline_value = labeled_match.group(2).strip()
            if inline_value:
                current_lines.append(inline_value)
            continue

        if current_key is not None:
            current_lines.append(stripped)

    flush()
    return sections


def _pick_single_value(sections: dict[str, str], field_name: str, fallback_text: str, default: str = "") -> str:
    title = _match_section_title(sections, field_name)
    if title:
        return _compact_single_value(sections[title])
    if field_name == "mission" and not sections:
        return _fallback_mission(fallback_text)
    return default


def _pick_list_values(sections: dict[str, str], field_name: str) -> tuple[str, ...]:
    title = _match_section_title(sections, field_name)
    if not title:
        return ()
    items = _extract_items(sections[title])
    return tuple(items)


def _match_section_title(sections: dict[str, str], field_name: str) -> str | None:
    labels = FIELD_LABELS[field_name]
    for title in sections:
        normalized = title.replace(" ", "")
        for label in labels:
            if label.replace(" ", "") in normalized:
                return title
    return None


def _compact_single_value(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""
    if len(lines) == 1:
        return lines[0]
    return "；".join(lines)


def _extract_items(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        bullet_match = re.match(r"^(?:[-*•]|[0-9]+[.)])\s*(.+)$", stripped)
        if bullet_match:
            item = bullet_match.group(1).strip()
        else:
            item = stripped
        for part in _split_inline_list_items(item):
            if part and part not in items:
                items.append(part)
    return items


def _split_inline_list_items(text: str) -> list[str]:
    parts = [part.strip(" ，,。；;") for part in re.split(r"[；;]\s*", text) if part.strip(" ，,。；;")]
    return parts or [text.strip()]


def _first_sentence(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped.split("。", 1)[0].strip(" ，,。")
    return ""


def _fallback_mission(text: str) -> str:
    cleaned = text.strip()
    for phrase in ("请初始化项目", "初始化项目", "初始化", "开始一个新项目"):
        cleaned = cleaned.replace(phrase, "")
    cleaned = cleaned.strip(" ，,。；;:：")
    if not cleaned:
        return ""
    if len(cleaned) <= 4 and cleaned in {"项目", "新项目", "方案"}:
        return ""
    return _first_sentence(cleaned)


def _compact_risk_list(missing_fields: tuple[str, ...]) -> list[str]:
    if not missing_fields:
        return []
    return [f"方案还有待补齐：{', '.join(missing_fields)}。"]


def _or_placeholder(value: str) -> str:
    return value.strip() or "待补充。"


def _split_decision(text: str) -> tuple[str, str, str]:
    cleaned = text.strip().strip("。；;")
    if not cleaned:
        return "待补充。", "待补充。", "待补充。"
    decision = cleaned
    reason = "待补充。"
    impact = "待补充。"

    for separator in ("因为", "由于", "原因是"):
        if separator in cleaned:
            left, right = cleaned.split(separator, 1)
            decision = left.strip(" ，,。；;")
            reason = right.strip(" ，,。；;") or reason
            break

    if "影响" in cleaned:
        parts = re.split(r"影响[：:]", cleaned, maxsplit=1)
        if len(parts) == 2:
            impact = parts[1].strip(" ，,。；;") or impact

    return decision or "待补充。", reason, impact
