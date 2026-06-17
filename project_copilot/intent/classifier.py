from __future__ import annotations

import re
from enum import Enum


class Intent(str, Enum):
    INIT_PROJECT = "init_project"
    ADOPT_PROJECT = "adopt_project"
    CONTINUE_DEV = "continue_development"
    CHECK_PROJECT = "check_project"
    END_WORK = "close_day"
    GENERATE_ROADMAP = "generate_roadmap"
    CHECK_OSS = "oss_check"
    PREPARE_OSS = "prepare_oss"
    GITHUB_SYNC = "github_sync"
    RELEASE_PROJECT = "release_project"
    PREPARE_RELEASE = "prepare_release"
    WHAT_DID_TODAY = "what_did_today"
    NEXT_STEP = "next_step"
    SUMMARIZE_PROJECT = "summarize_project"
    SYNC_PROJECT_STATE = "sync_project_state"
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
    (
        Intent.GITHUB_SYNC,
        (
            "同步github",
            "同步到github",
            "同步到 github",
            "执行同步",
            "发布到github",
            "发布到 github",
            "开源到github",
            "开源到 github",
            "私有同步",
            "备份到云端",
            "云端备份",
            "github sync",
            "push to github",
        ),
    ),
    (Intent.PREPARE_OSS, ("准备开源", "开源发布准备", "完善开源", "prepare oss", "prepare open source")),
    (Intent.CHECK_OSS, ("oss", "开源准备", "开源检查", "readiness")),
    (
        Intent.RELEASE_PROJECT,
        (
            "一键发布",
            "创建 release",
            "创建 github release",
            "发布版本",
            "发布 alpha",
            "版本标记",
            "release project",
            "github release",
        ),
    ),
    (Intent.PREPARE_RELEASE, ("准备发布", "发布", "release")),
    (Intent.GENERATE_ROADMAP, ("生成路线图",)),
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
    (Intent.CHECK_PROJECT, ("检查项目", "项目状态", "项目怎么样", "健康度", "check project", "status")),
]


def classify_intent(text: str) -> Intent:
    normalized = text.strip().lower()
    if not normalized:
        return Intent.UNKNOWN
    if _looks_like_release_request(normalized):
        return Intent.RELEASE_PROJECT

    for intent, keywords in KEYWORDS:
        if any(keyword.lower() in normalized for keyword in keywords):
            return intent
    return Intent.UNKNOWN


def classify_intent_name(text: str) -> str:
    return classify_intent(text).value


def _looks_like_release_request(text: str) -> bool:
    if "发布" not in text and "release" not in text:
        return False
    return re.search(r"\bv?\d+\.\d+\.\d+(?:[-.][0-9a-z.-]+)?\b", text) is not None
