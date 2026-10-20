"""HTTP-API: inkomende kanaalberichten, werkbonnen en goedkeuringen."""

import base64

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from .approvals import ApprovalError
from .channels.base import InboundAttachment, InboundMessage, OutboundMessage
from .config import settings
from .container import Container, build_container
from .models import Approval, ApprovalStatus, Job


class AttachmentIn(BaseModel):
    filename: str
    media_type: str
    data_b64: str


class MessageIn(BaseModel):
    sender: str
    text: str = ""
    attachments: list[AttachmentIn] = []


class Decision(BaseModel):
    approve: bool
    user: str


def create_app(container: Container | None = None) -> FastAPI:
    container = container or build_container(settings)
    app = FastAPI(title="HVAC Automation Agent")
    app.state.container = container

    @app.post("/tenants/{tenant_id}/channels/{channel}/inbound")
    def inbound(tenant_id: int, channel: str, body: MessageIn):
        if channel not in container.channels:
            raise HTTPException(404, f"Kanaal '{channel}' niet actief")
        message = InboundMessage(
            tenant_id=tenant_id,
            channel=channel,
            sender=body.sender,
            text=body.text,
            attachments=[
                InboundAttachment(filename=a.filename, media_type=a.media_type, data=base64.b64decode(a.data_b64))
                for a in body.attachments
            ],
        )
        with container.sessions.begin() as session:
            result = container.work_orders.handle(session, message)
            container.channels[channel].send(OutboundMessage(channel=channel, recipient=body.sender, text=result.reply))
            return {"reply": result.reply, "missing": result.missing}

    @app.get("/jobs/{job_id}/work-order")
    def work_order(job_id: int):
        with container.sessions() as session:
            job = session.get(Job, job_id)
            if job is None or job.work_order is None:
                raise HTTPException(404, "Geen werkbon voor deze klus")
            wo = job.work_order
            return {"job_id": job.id, "status": wo.status, "items": wo.items, "notes": wo.notes}

    @app.get("/tenants/{tenant_id}/approvals")
    def approvals(tenant_id: int, status: str = ApprovalStatus.PENDING):
        with container.sessions() as session:
            rows = session.scalars(
                select(Approval).where(Approval.tenant_id == tenant_id, Approval.status == status)
            ).all()
            return [{"id": a.id, "kind": a.kind, "payload": a.payload, "status": a.status} for a in rows]

    @app.post("/approvals/{approval_id}/decision")
    def decide(approval_id: int, body: Decision):
        with container.sessions.begin() as session:
            approval = session.get(Approval, approval_id)
            if approval is None:
                raise HTTPException(404, "Goedkeuring niet gevonden")
            try:
                container.approvals.decide(session, approval, body.approve, body.user)
            except ApprovalError as e:
                raise HTTPException(409, str(e))
            return {"id": approval.id, "status": approval.status, "result": approval.result}

    return app
