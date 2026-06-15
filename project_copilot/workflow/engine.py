from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from project_copilot.intent import classify_intent_name
from project_copilot.workflow import (
    adopt_project,
    check_project,
    close_day,
    continue_development,
    github_sync,
    init_project,
    oss_check,
    prepare_oss,
)
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

    def register(self, intent_name: str, handler: WorkflowHandler) -> None:
        self._registry[intent_name] = handler

    def dispatch(self, root: Path, text: str, intent_name: str) -> WorkflowResult:
        context = WorkflowContext(root=root, text=text, intent_name=intent_name)
        handler = self._registry.get(intent_name, check_project.run)
        return handler(context)

    def run(self, root: Path, text: str) -> WorkflowResult:
        intent_name = classify_intent_name(text)
        return self.dispatch(root=root, text=text, intent_name=intent_name)

    @property
    def registered_intents(self) -> tuple[str, ...]:
        return tuple(self._registry)


def run_structured_workflow(root: Path, text: str) -> WorkflowResult:
    return WorkflowEngine().run(root, text)


def run_text_workflow(root: Path, text: str) -> str:
    return run_structured_workflow(root, text).render()
