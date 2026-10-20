"""Kanaal-gateway: elk kanaal (WhatsApp, e-mail, app, webportaal) zet berichten om
naar dit uniforme formaat, zodat workflows kanaal-onafhankelijk zijn."""

from typing import Protocol

from pydantic import BaseModel


class InboundAttachment(BaseModel):
    filename: str
    media_type: str
    data: bytes


class InboundMessage(BaseModel):
    tenant_id: int
    channel: str
    sender: str  # telefoonnummer of e-mailadres
    text: str = ""
    attachments: list[InboundAttachment] = []


class OutboundMessage(BaseModel):
    channel: str
    recipient: str
    text: str


class Channel(Protocol):
    name: str

    def send(self, message: OutboundMessage) -> None: ...
