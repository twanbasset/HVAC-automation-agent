"""W4 — Werkbon & foto's compleet.

Monteur stuurt foto's en berichten vanaf de klus; de agent koppelt ze aan de checklist,
meldt direct wat ontbreekt of onbruikbaar is, en zet een complete werkbon door naar
Syntess plus een factuurconcept ter goedkeuring (Exact)."""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from ..audit import audit
from ..channels.base import InboundMessage
from ..checklists import Checklist, ItemKind
from ..integrations.base import FieldServiceSystem, WorkOrderSubmission
from ..llm import LLM
from ..models import Approval, Attachment, Job, JobStatus, Technician, WorkOrder, WorkOrderStatus

ACTOR = "agent:werkbon"


@dataclass
class WorkOrderResult:
    reply: str
    work_order: WorkOrder | None = None
    missing: list[str] | None = None


class WorkOrderWorkflow:
    def __init__(self, llm: LLM, checklists: dict[str, Checklist], field_service: FieldServiceSystem):
        self.llm = llm
        self.checklists = checklists
        self.field_service = field_service

    def handle(self, session: Session, message: InboundMessage) -> WorkOrderResult:
        technician = session.scalar(
            select(Technician).where(Technician.tenant_id == message.tenant_id, Technician.phone == message.sender)
        )
        if technician is None:
            return WorkOrderResult("Dit nummer is niet bekend als monteur. Neem contact op met kantoor.")
        job = session.scalar(
            select(Job)
            .where(Job.technician_id == technician.id, Job.status == JobStatus.IN_PROGRESS)
            .order_by(Job.id.desc())
        )
        if job is None:
            return WorkOrderResult("Je hebt geen klus in uitvoering. Start de klus eerst in de planning.")
        checklist = self.checklists.get(job.job_type)
        if checklist is None:
            return WorkOrderResult(f"Geen checklist voor klustype '{job.job_type}'. Kantoor is op de hoogte.")

        work_order = job.work_order or self._create_work_order(session, job, checklist)
        if work_order.status != WorkOrderStatus.OPEN:
            return WorkOrderResult("Deze werkbon is al compleet en doorgezet.", work_order)

        feedback: list[str] = []
        for attachment in message.attachments:
            feedback.append(self._handle_photo(session, work_order, checklist, attachment, message.text))

        finished_claimed = False
        # Bij foto's is de tekst het bijschrift; alleen losse tekst bevat meetwaarden.
        if message.text and not message.attachments:
            finished_claimed, text_feedback = self._handle_text(work_order, checklist, message.text)
            feedback.extend(text_feedback)

        flag_modified(work_order, "items")
        flag_modified(work_order, "notes")
        missing = [i.label for i in checklist.items if not work_order.items[i.key]["done"]]

        if not missing:
            reference = self._submit(session, job, work_order)
            feedback.append(f"✅ Werkbon compleet en doorgezet ({reference}). Bedankt, je kunt vertrekken!")
        elif finished_claimed:
            feedback.append("⚠️ Nog niet vertrekken, de werkbon is niet compleet. Nog nodig:")
            feedback.extend(f"• {label}" for label in missing)
        else:
            feedback.append(f"Nog {len(missing)} item(s) open: " + ", ".join(missing))

        return WorkOrderResult("\n".join(f for f in feedback if f), work_order, missing)

    def _create_work_order(self, session: Session, job: Job, checklist: Checklist) -> WorkOrder:
        items = {i.key: {"done": False, "value": None, "extracted": {}, "attachment_ids": []} for i in checklist.items}
        work_order = WorkOrder(job=job, items=items, notes=[])
        session.add(work_order)
        session.flush()
        audit(session, job.tenant_id, ACTOR, "werkbon_aangemaakt", job_id=job.id)
        return work_order

    def _handle_photo(self, session, work_order, checklist, attachment, caption) -> str:
        analysis = self.llm.analyze_photo(
            attachment.data, attachment.media_type, caption or None, checklist.items_of(ItemKind.PHOTO)
        )
        item = checklist.item(analysis.matched_item_key) if analysis.matched_item_key else None
        stored = Attachment(
            work_order=work_order,
            filename=attachment.filename,
            media_type=attachment.media_type,
            data=attachment.data,
            item_key=item.key if item else None,
            analysis=analysis.model_dump(),
        )
        session.add(stored)
        session.flush()
        audit(session, work_order.job.tenant_id, ACTOR, "foto_beoordeeld", attachment_id=stored.id, **analysis.model_dump())

        if item is None or item.kind != ItemKind.PHOTO:
            return f"❓ Ik kan '{attachment.filename}' niet aan de checklist koppelen. Zet in het bijschrift wat het is."
        if not analysis.is_usable:
            return f"❌ {item.label}: {analysis.issue or 'niet bruikbaar'}. Maak een nieuwe foto."

        state = work_order.items[item.key]
        state["done"] = True
        state["attachment_ids"].append(stored.id)
        state["extracted"].update({f.name: f.value for f in analysis.extracted})
        details = ", ".join(f"{f.name}: {f.value}" for f in analysis.extracted)
        return f"✔ {item.label}" + (f" ({details})" if details else "")

    def _handle_text(self, work_order, checklist, text) -> tuple[bool, list[str]]:
        extraction = self.llm.extract_text(text, checklist.items_of(ItemKind.MEASUREMENT))
        feedback = []
        for m in extraction.measurements:
            item = checklist.item(m.item_key)
            if item is None or item.kind != ItemKind.MEASUREMENT:
                continue
            work_order.items[item.key].update(done=True, value=m.value)
            feedback.append(f"✔ {item.label}: {m.value}")
        if extraction.customer_signed:
            for item in checklist.items_of(ItemKind.CONFIRMATION):
                work_order.items[item.key]["done"] = True
                feedback.append(f"✔ {item.label}")
        if extraction.notes:
            work_order.notes.append(extraction.notes)
        return extraction.job_finished_claimed, feedback

    def _submit(self, session: Session, job: Job, work_order: WorkOrder) -> str:
        submission = WorkOrderSubmission(
            job_ref=job.external_ref,
            job_type=job.job_type,
            items=work_order.items,
            notes=work_order.notes,
            attachments=[
                {"filename": a.filename, "media_type": a.media_type, "item_key": a.item_key}
                for a in work_order.attachments
                if a.item_key
            ],
        )
        reference = self.field_service.submit_work_order(submission)
        work_order.status = WorkOrderStatus.SUBMITTED
        job.status = JobStatus.DONE
        session.add(
            Approval(
                tenant_id=job.tenant_id,
                kind="factuur_concept",
                payload={
                    "job_id": job.id,
                    "customer_name": job.customer_name,
                    "reference": job.external_ref,
                    "lines": job.invoice_lines,
                },
            )
        )
        audit(session, job.tenant_id, ACTOR, "werkbon_ingediend", job_id=job.id, syntess_ref=reference)
        return reference
