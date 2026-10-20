"""Mock-implementaties om te bouwen en testen zonder toegang tot Syntess/Exact."""

from .base import DraftInvoice, WorkOrderSubmission


class MockSyntess:
    def __init__(self):
        self.work_orders: list[WorkOrderSubmission] = []

    def submit_work_order(self, submission: WorkOrderSubmission) -> str:
        self.work_orders.append(submission)
        return f"SYN-WB-{len(self.work_orders):05d}"


class MockExact:
    def __init__(self):
        self.invoices: list[DraftInvoice] = []

    def create_draft_invoice(self, invoice: DraftInvoice) -> str:
        self.invoices.append(invoice)
        return f"EXACT-CONCEPT-{len(self.invoices):05d}"
