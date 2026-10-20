import pytest
from fastapi.testclient import TestClient

from hvac_agent.app import create_app
from hvac_agent.channels.outbox import OutboxChannel
from hvac_agent.checklists import load_checklists
from hvac_agent.config import ROOT
from hvac_agent.container import Container
from hvac_agent.db import make_session_factory
from hvac_agent.integrations.mock import MockExact, MockSyntess
from hvac_agent.llm.fake import FakeLLM
from hvac_agent.seed import seed


@pytest.fixture
def container():
    return Container(
        sessions=make_session_factory("sqlite://"),
        llm=FakeLLM(),
        checklists=load_checklists(ROOT / "config" / "checklists"),
        field_service=MockSyntess(),
        accounting=MockExact(),
        channels={"app": OutboxChannel("app")},
    )


@pytest.fixture
def job(container):
    with container.sessions.begin() as session:
        return seed(session)


@pytest.fixture
def client(container):
    return TestClient(create_app(container))
