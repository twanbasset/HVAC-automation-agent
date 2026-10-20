"""Regelgebaseerde nep-LLM voor tests en demo's zonder API-sleutel.
Herkent items aan trefwoorden in bijschrift/bestandsnaam en waarden via regex."""

import re

from ..checklists import ChecklistItem, ItemKind
from .base import ExtractedField, MeasurementValue, PhotoAnalysis, TextExtraction

KEYWORDS = {
    "typeplaatje": ["typeplaatje", "typeplaat", "serienummer"],
    "buitenunit": ["buitenunit", "buitendeel"],
    "binnenunit": ["binnenunit", "binnendeel", "hydrobox"],
    "leidingwerk": ["leiding", "isolatie"],
    "meterkast": ["meterkast", "groep"],
    "condensafvoer": ["condens"],
    "ketel_open": ["brander", "geopend", "open"],
    "na_afronding": ["gesloten", "afgerond", "na afronding"],
    "vacuumtest": ["vacuum", "vacuüm"],
    "druktest": ["druktest", "stikstof"],
    "koudemiddel": ["koudemiddel", "bijgevuld"],
    "rookgasmeting": ["rookgas", "co2"],
    "waterdruk": ["waterdruk"],
}


def _match(text: str, items: list[ChecklistItem]) -> ChecklistItem | None:
    """Kies het item waarvan de meeste trefwoord-groepen in de tekst voorkomen;
    groepen in de key die níet in de tekst staan tellen negatief."""
    text = text.lower()
    best, best_score = None, 0.0
    for item in items:
        fragments = [f for f in KEYWORDS if f in item.key]
        hits = sum(any(w in text for w in KEYWORDS[f]) for f in fragments)
        score = hits - 0.5 * (len(fragments) - hits)
        if hits and score > best_score:
            best, best_score = item, score
    return best


class FakeLLM:
    def analyze_photo(
        self, image: bytes, media_type: str, caption: str | None, items: list[ChecklistItem]
    ) -> PhotoAnalysis:
        text = caption or ""
        item = _match(text, items)
        if item is None:
            return PhotoAnalysis(matched_item_key=None, is_usable=False, issue="Onbekend wat deze foto toont", extracted=[])
        if "wazig" in text.lower():
            return PhotoAnalysis(matched_item_key=item.key, is_usable=False, issue="Foto is wazig, maak een nieuwe", extracted=[])
        extracted = [ExtractedField(name=f, value=f"{f}-uit-foto") for f in item.extract]
        return PhotoAnalysis(matched_item_key=item.key, is_usable=True, issue=None, extracted=extracted)

    def extract_text(self, text: str, items: list[ChecklistItem]) -> TextExtraction:
        measurements = []
        for sentence in re.split(r"[.\n;]", text):
            item = _match(sentence, [i for i in items if i.kind == ItemKind.MEASUREMENT])
            number = re.search(r"\d+(?:[.,]\d+)?\s*\w*", sentence)
            if item and number:
                measurements.append(MeasurementValue(item_key=item.key, value=number.group().strip()))
        lower = text.lower()
        return TextExtraction(
            measurements=measurements,
            customer_signed=any(w in lower for w in ["getekend", "handtekening", "akkoord"]),
            job_finished_claimed=any(w in lower for w in ["klaar", "vertrek", "afgerond"]),
            notes=None,
        )
