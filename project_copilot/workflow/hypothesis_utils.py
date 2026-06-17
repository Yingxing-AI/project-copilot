from __future__ import annotations

UNCERTAIN_MARKERS = (
    "可能",
    "也许",
    "大概",
    "估计",
    "推测",
    "猜测",
    "看起来",
    "暂时",
    "先猜",
    "待验证",
    "待确认",
    "候选",
    "试试",
    "考虑",
)


def looks_uncertain(text: str) -> bool:
    normalized = text.strip().lower()
    return any(marker in normalized for marker in UNCERTAIN_MARKERS)
