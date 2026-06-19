from __future__ import annotations

from enum import Enum


class Intent(str, Enum):
    INIT_PROJECT = "init_project"
    ADOPT_PROJECT = "adopt_project"
    CONTINUE_DEV = "continue_development"
    CHECK_PROJECT = "check_project"
    END_WORK = "close_day"
    WHAT_DID_TODAY = "what_did_today"
    NEXT_STEP = "next_step"
    SUMMARIZE_PROJECT = "summarize_project"
    SYNC_PROJECT_STATE = "sync_project_state"
    REFRESH_VALIDATION_REPORT = "refresh_validation_report"
    EXPORT_VALIDATION_SNAPSHOT = "export_validation_snapshot"
    REVIEW_PROJECT = "review_project"
    TIMELINE_PROJECT = "timeline_project"
    DRIFT_CHECK = "drift_check"
    RECORD_DECISION = "record_decision"
    SHOW_ROADMAP = "show_roadmap"
    UNKNOWN = "unknown"


KEYWORDS: list[tuple[Intent, tuple[str, ...]]] = [
    (
        Intent.ADOPT_PROJECT,
        ("接管", "已有项目", "现有项目", "开发到一半", "纳入", "初始化记忆", "adopt"),
    ),
    (Intent.INIT_PROJECT, ("初始化", "创建项目", "新项目", "开始一个新项目", "init", "start project")),
    (Intent.CONTINUE_DEV, ("继续开发", "接着做", "恢复开发", "continue")),
    (Intent.END_WORK, ("结束工作", "下班", "今天结束", "收工", "end work")),
    (Intent.REVIEW_PROJECT, ("项目复盘", "复盘项目", "review")),
    (Intent.TIMELINE_PROJECT, ("项目时间轴", "时间轴", "timeline")),
    (Intent.DRIFT_CHECK, ("项目偏航检查", "偏航检查", "检查偏航", "是否跑偏", "drift")),
    (Intent.RECORD_DECISION, ("记录决策", "保存决策", "新增决策", "decision")),
    (Intent.SHOW_ROADMAP, ("查看路线图", "看路线图", "路线图", "roadmap")),
    (Intent.WHAT_DID_TODAY, ("今天做了什么", "今日变更", "what did")),
    (Intent.NEXT_STEP, ("下一步", "现在应该做什么", "next")),
    (Intent.SUMMARIZE_PROJECT, ("总结项目", "项目总结", "summary")),
    (
        Intent.SYNC_PROJECT_STATE,
        (
            "同步项目状态",
            "更新项目状态",
            "同步文档",
            "更新文档",
            "同步 roadmap",
            "同步 changelog",
            "sync project state",
            "sync docs",
        ),
    ),
    (
        Intent.REFRESH_VALIDATION_REPORT,
        (
            "刷新验证报告",
            "同步验证报告",
            "更新验证报告",
            "刷新验证汇总",
            "refresh validation report",
        ),
    ),
    (
        Intent.EXPORT_VALIDATION_SNAPSHOT,
        (
            "导出验证快照",
            "刷新验证快照",
            "生成验证快照",
            "export validation snapshot",
        ),
    ),
    (Intent.CHECK_PROJECT, ("检查项目", "项目状态", "项目怎么样", "健康度", "check project", "status")),
]


def classify_intent(text: str) -> Intent:
    normalized = text.strip().lower()
    if not normalized:
        return Intent.UNKNOWN
    if _looks_like_initial_project_proposal(normalized):
        return Intent.INIT_PROJECT

    for intent, keywords in KEYWORDS:
        if any(keyword.lower() in normalized for keyword in keywords):
            return intent
    return Intent.UNKNOWN


def classify_intent_name(text: str) -> str:
    return classify_intent(text).value


def _looks_like_initial_project_proposal(text: str) -> bool:
    markers = (
        "项目使命",
        "目标用户",
        "商业目标",
        "mvp 范围",
        "mvp范围",
        "技术栈",
        "当前阶段",
        "初始 roadmap",
        "初始 roadmap",
        "初始 decisions",
        "初始 decisions",
    )
    hits = sum(1 for marker in markers if marker in text)
    if hits >= 2:
        return True
    return "项目使命" in text and any(marker in text for marker in ("目标用户", "商业目标", "技术栈", "mvp", "roadmap", "decisions"))
