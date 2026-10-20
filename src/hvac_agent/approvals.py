"""Afhandeling van goedkeuringen (human-in-the-loop)."""

from sqlalchemy.orm import Session

from .audit import audit
from .integrations.base import AccountingSystem, DraftInvoice, InvoiceLine
from .models import Approval, ApprovalStatus


class ApprovalError(Exception):
    pass


class ApprovalService:
    def __init__(self, accounting: AccountingSystem):
        self.accounting = accounting

    def decide(self, session: Session, approval: Approval, approve: bool, user: str) -> Approval:
        if approval.status != ApprovalStatus.PENDING:
            raise ApprovalError(f"Goedkeuring {approval.id} is al {approval.status}")
        if not approve:
            approval.status = ApprovalStatus.REJECTED
        elif approval.kind == "factuur_concept":
            p = approval.payload
            invoice = DraftInvoice(
                customer_name=p["customer_name"],
                reference=p["reference"],
                lines=[
                    InvoiceLine(description=line["omschrijving"], quantity=line["aantal"], unit_price=line["prijs"])
                    for line in p["lines"]
                ],
            )
            approval.result = {"exact_ref": self.accounting.create_draft_invoice(invoice)}
            approval.status = ApprovalStatus.APPROVED
        else:
            raise ApprovalError(f"Onbekend type goedkeuring: {approval.kind}")
        audit(session, approval.tenant_id, f"gebruiker:{user}", f"goedkeuring_{approval.status}", approval_id=approval.id)
        return approval
