from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from project_copilot.intent import classify_intent_name
from project_copilot.workflow.adopt_project import run as adopt_project
from project_copilot.workflow.check_project import run as check_project
from project_copilot.workflow.close_day import run as close_day
from project_copilot.workflow.continue_development import run as continue_development
from project_copilot.workflow.drift_check import run as drift_check
from project_copilot.workflow.export_validation_snapshot import run as export_validation_snapshot
from project_copilot.workflow.init_project import run as init_project
from project_copilot.workflow.record_decision import run as record_decision
from project_copilot.workflow.refresh_validation_report import run as refresh_validation_report
from project_copilot.workflow.review_project import run as review_project
from project_copilot.workflow.show_roadmap import run as show_roadmap
from project_copilot.workflow.sync_project_state import run as sync_project_state
from project_copilot.workflow.timeline_project import run as timeline_project
from project_copilot.workflow.root import resolve_project_root
from project_copilot.workflow.types import WorkflowContext, WorkflowResult

WorkflowHandler = Callable[[WorkflowContext], WorkflowResult]


class WorkflowEngine:
    def __init__(self) -> None:
        self._registry: dict[str, WorkflowHandler] = {}
        self.register("init_project", init_project)
        self.register("check_project", check_project)
        self.register("continue_development", continue_development)
        self.register("close_day", close_day)
        self.register("adopt_project", adopt_project)
        self.register("sync_project_state", sync_project_state)
        self.register("review_project", review_project)
        self.register("timeline_project", timeline_project)
        self.register("refresh_validation_report", refresh_validation_report)
        self.register("export_validation_snapshot", export_validation_snapshot)
        self.register("drift_check", drift_check)
        self.register("record_decision", record_decision)
        self.register("show_roadmap", show_roadmap)

    def register(self, intent_name: str, handler: WorkflowHandler) -> None:
        self._registry[intent_name] = handler

    def dispatch(self, root: Path, text: str, intent_name: str) -> WorkflowResult:
        root = resolve_project_root(root)
        context = WorkflowContext(root=root, text=text, intent_name=intent_name)
        if intent_name == "unknown":
            return _unknown_intent_result(context)
        handler = self._registry.get(intent_name, check_project)
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
            "刷新验证报告",
            "同步项目状态",
            "导出验证快照",
        ],
    )
