from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from project_copilot.intent import classify_intent_name
from project_copilot.workflow import (
    adopt_project,
    check_project,
    close_day,
    continue_development,
    drift_check,
    github_sync,
    init_project,
    oss_check,
    prepare_oss,
    record_decision,
    release_project,
    review_project,
    show_roadmap,
    sync_project_state,
    timeline_project,
)
from project_copilot.workflow.root import resolve_project_root
from project_copilot.workflow.types import WorkflowContext, WorkflowResult

WorkflowHandler = Callable[[WorkflowContext], WorkflowResult]


class WorkflowEngine:
    def __init__(self) -> None:
        self._registry: dict[str, WorkflowHandler] = {}
        self.register("init_project", init_project.run)
        self.register("check_project", check_project.run)
        self.register("continue_development", continue_development.run)
        self.register("close_day", close_day.run)
        self.register("oss_check", oss_check.run)
        self.register("prepare_oss", prepare_oss.run)
        self.register("github_sync", github_sync.run)
        self.register("adopt_project", adopt_project.run)
        self.register("sync_project_state", sync_project_state.run)
        self.register("release_project", release_project.run)
        self.register("review_project", review_project.run)
        self.register("timeline_project", timeline_project.run)
        self.register("drift_check", drift_check.run)
        self.register("record_decision", record_decision.run)
        self.register("show_roadmap", show_roadmap.run)

    def register(self, intent_name: str, handler: WorkflowHandler) -> None:
        self._registry[intent_name] = handler

    def dispatch(self, root: Path, text: str, intent_name: str) -> WorkflowResult:
        root = resolve_project_root(root)
        context = WorkflowContext(root=root, text=text, intent_name=intent_name)
        if intent_name == "unknown":
            return _unknown_intent_result(context)
        handler = self._registry.get(intent_name, check_project.run)
        return handler(context)

    def run(self, root: Path, text: str) -> WorkflowResult:
        root = resolve_project_root(root)
        intent_name = classify_intent_name(text)
        return self.dispatch(root=root, text=text, intent_name=intent_name)

    @property
    def registered_intents(self) -> tuple[str, ...]:
        return tuple(self._registry)


def run_structured_workflow(root: Path, text: str) -> WorkflowResult:
    return WorkflowEngine().run(root, text)


def run_text_workflow(root: Path, text: str) -> str:
    return run_structured_workflow(root, text).render()


def _unknown_intent_result(context: WorkflowContext) -> WorkflowResult:
    return WorkflowResult(
        intent_name=context.intent_name,
        status="needs_input",
        title="暂时没有识别这个意图。",
        summary="可以换一种说法，或直接输入下面这些常用操作。",
        details={
            "原始输入": context.text.strip(),
        },
        next_steps=[
            "检查项目",
            "继续开发项目",
            "今天结束工作",
            "项目复盘",
            "项目时间轴",
            "项目偏航检查",
            "记录决策",
            "备份到云端",
            "同步项目状态",
            "发布版本 v0.3.0-beta.1",
        ],
    )
