from .base import OutboundMessage


class OutboxChannel:
    """Bewaart uitgaande berichten. Gebruikt voor het generieke/app-kanaal (antwoord gaat
    terug in de HTTP-response) en in tests. WhatsApp/e-mail-adapters volgen later."""

    def __init__(self, name: str):
        self.name = name
        self.sent: list[OutboundMessage] = []

    def send(self, message: OutboundMessage) -> None:
        self.sent.append(message)
