from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base


def make_session_factory(database_url: str) -> sessionmaker[Session]:
    kwargs = {}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if database_url in ("sqlite://", "sqlite:///:memory:"):
            kwargs["poolclass"] = StaticPool
    engine = create_engine(database_url, **kwargs)
    # MVP: tabellen direct aanmaken; later Alembic-migraties.
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)
