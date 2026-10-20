"""Samenstellen van de afhankelijkheden (LLM, integraties, kanalen)."""

from dataclasses import dataclass, field

from sqlalchemy.orm import Session, sessionmaker

from .approvals import ApprovalService
from .channels.base import Channel
from .channels.outbox import OutboxChannel
from .checklists import Checklist, load_checklists
from .config import Settings
from .db import make_session_factory
from .integrations.base import AccountingSystem, FieldServiceSystem
from .integrations.mock import MockExact, MockSyntess
from .llm import LLM
from .workflows.work_order import WorkOrderWorkflow


@dataclass
class Container:
    sessions: sessionmaker[Session]
    llm: LLM
    checklists: dict[str, Checklist]
    field_service: FieldServiceSystem
    accounting: AccountingSystem
    channels: dict[str, Channel] = field(default_factory=dict)

    @property
    def work_orders(self) -> WorkOrderWorkflow:
        return WorkOrderWorkflow(self.llm, self.checklists, self.field_service)

    @property
    def approvals(self) -> ApprovalService:
        return ApprovalService(self.accounting)


def build_container(settings: Settings) -> Container:
    if settings.anthropic_api_key:
        from .llm.claude import ClaudeLLM

        llm: LLM = ClaudeLLM(settings.llm_model, settings.anthropic_api_key)
    else:
        from .llm.fake import FakeLLM

        llm = FakeLLM()
    if settings.syntess_mode != "mock" or settings.exact_mode != "mock":
        raise NotImplementedError("Live Syntess/Exact-koppelingen volgen in een latere stap")
    return Container(
        sessions=make_session_factory(settings.database_url),
        llm=llm,
        checklists=load_checklists(settings.checklist_dir),
        field_service=MockSyntess(),
        accounting=MockExact(),
        channels={"app": OutboxChannel("app")},
    )
