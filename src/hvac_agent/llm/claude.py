"""Claude-implementatie via de Anthropic SDK met gestructureerde output."""

import base64

import anthropic

from ..checklists import ChecklistItem
from .base import PhotoAnalysis, TextExtraction

SYSTEM = (
    "Je bent de werkbon-assistent van een HVAC-installatiebedrijf (warmtepompen, airco, cv). "
    "Monteurs sturen foto's en berichten vanaf de klus. Jij koppelt ze aan de checklist van de "
    "werkbon. Wees streng op bruikbaarheid: foto's dienen als bewijs voor garantie, "
    "F-gassenregistratie en subsidie. Verzin nooit waarden die niet zichtbaar of genoemd zijn. "
    "Schrijf uitleg voor monteurs in kort, direct Nederlands."
)


def _describe(items: list[ChecklistItem]) -> str:
    lines = []
    for i in items:
        extra = f" (lees af: {', '.join(i.extract)})" if i.extract else ""
        lines.append(f"- {i.key}: {i.label}{extra}")
    return "\n".join(lines)


class ClaudeLLM:
    def __init__(self, model: str, api_key: str | None = None, client: anthropic.Anthropic | None = None):
        self.model = model
        self.client = client or anthropic.Anthropic(api_key=api_key or None)

    def analyze_photo(
        self, image: bytes, media_type: str, caption: str | None, items: list[ChecklistItem]
    ) -> PhotoAnalysis:
        prompt = (
            "Welk checklist-item toont deze foto? Mogelijke items:\n"
            f"{_describe(items)}\n\n"
            f"Bijschrift van de monteur: {caption or '(geen)'}"
        )
        response = self.client.messages.parse(
            model=self.model,
            max_tokens=4000,
            system=SYSTEM,
            output_config={"effort": "medium"},
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": base64.standard_b64encode(image).decode(),
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }],
            output_format=PhotoAnalysis,
        )
        return self._parsed(response, PhotoAnalysis)

    def extract_text(self, text: str, items: list[ChecklistItem]) -> TextExtraction:
        prompt = (
            "Haal uit dit bericht van de monteur de meetwaarden voor deze checklist-items:\n"
            f"{_describe(items)}\n\nBericht:\n{text}"
        )
        response = self.client.messages.parse(
            model=self.model,
            max_tokens=4000,
            system=SYSTEM,
            output_config={"effort": "low"},
            messages=[{"role": "user", "content": prompt}],
            output_format=TextExtraction,
        )
        return self._parsed(response, TextExtraction)

    @staticmethod
    def _parsed(response, model_cls):
        if response.stop_reason == "refusal" or response.parsed_output is None:
            raise RuntimeError(f"Geen bruikbaar antwoord van het model (stop_reason={response.stop_reason})")
        return response.parsed_output
