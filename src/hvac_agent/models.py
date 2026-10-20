"""Domeinmodel (kern). Zie docs/03-architectuur.md."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import JSON, ForeignKey, LargeBinary, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    """Een installatiebedrijf dat het platform gebruikt."""

    __tablename__ = "tenants"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))


class Technician(Base):
    __tablename__ = "technicians"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    name: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str] = mapped_column(String(32), index=True)
    skills: Mapped[list] = mapped_column(JSON, default=list)


class JobStatus(StrEnum):
    PLANNED = "gepland"
    IN_PROGRESS = "in_uitvoering"
    DONE = "afgerond"


class Job(Base):
    """Een klus (installatie, onderhoud, storing) — bron is Syntess."""

    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    external_ref: Mapped[str] = mapped_column(String(64))  # projectnummer in Syntess
    job_type: Mapped[str] = mapped_column(String(64))
    customer_name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str] = mapped_column(String(300))
    technician_id: Mapped[int | None] = mapped_column(ForeignKey("technicians.id"))
    status: Mapped[str] = mapped_column(String(32), default=JobStatus.PLANNED)
    # Factuurregels uit de offerte: [{"omschrijving", "aantal", "prijs"}]
    invoice_lines: Mapped[list] = mapped_column(JSON, default=list)

    technician: Mapped[Technician | None] = relationship()
    work_order: Mapped["WorkOrder | None"] = relationship(back_populates="job")


class WorkOrderStatus(StrEnum):
    OPEN = "open"
    COMPLETE = "compleet"
    SUBMITTED = "ingediend"


class WorkOrder(Base):
    """Werkbon. `items` houdt per checklist-item de status bij:
    {key: {"done": bool, "value": str|None, "extracted": {...}, "attachment_ids": [...]}}"""

    __tablename__ = "work_orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), unique=True)
    status: Mapped[str] = mapped_column(String(32), default=WorkOrderStatus.OPEN)
    items: Mapped[dict] = mapped_column(JSON, default=dict)
    notes: Mapped[list] = mapped_column(JSON, default=list)

    job: Mapped[Job] = relationship(back_populates="work_order")
    attachments: Mapped[list["Attachment"]] = relationship(back_populates="work_order")


class Attachment(Base):
    """Foto of document. MVP: in de database; later S3-compatible opslag (EU)."""

    __tablename__ = "attachments"
    id: Mapped[int] = mapped_column(primary_key=True)
    work_order_id: Mapped[int] = mapped_column(ForeignKey("work_orders.id"))
    filename: Mapped[str] = mapped_column(String(255))
    media_type: Mapped[str] = mapped_column(String(64))
    data: Mapped[bytes] = mapped_column(LargeBinary)
    item_key: Mapped[str | None] = mapped_column(String(64))
    analysis: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    work_order: Mapped[WorkOrder] = relationship(back_populates="attachments")


class ApprovalStatus(StrEnum):
    PENDING = "open"
    APPROVED = "goedgekeurd"
    REJECTED = "afgewezen"


class Approval(Base):
    """Human-in-the-loop: acties die geld raken of naar de klant gaan."""

    __tablename__ = "approvals"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    kind: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32), default=ApprovalStatus.PENDING)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    actor: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(100))
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
