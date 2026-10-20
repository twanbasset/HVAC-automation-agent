"""Interfaces naar externe systemen. Syntess en Exact zijn de eerste implementaties;
andere pakketten (Gripp, Simpro, Moneybird, ...) kunnen later naast deze interfaces."""

from typing import Protocol

from pydantic import BaseModel


class WorkOrderSubmission(BaseModel):
    job_ref: str
    job_type: str
    items: dict
    notes: list[str]
    attachments: list[dict]  # [{"filename", "media_type", "item_key"}]


class InvoiceLine(BaseModel):
    description: str
    quantity: float
    unit_price: float


class DraftInvoice(BaseModel):
    customer_name: str
    reference: str
    lines: list[InvoiceLine]


class FieldServiceSystem(Protocol):
    """Projecten, planning en werkbonnen (Syntess)."""

    def submit_work_order(self, submission: WorkOrderSubmission) -> str: ...


class AccountingSystem(Protocol):
    """Boekhouding en facturatie (Exact Online)."""

    def create_draft_invoice(self, invoice: DraftInvoice) -> str: ...
