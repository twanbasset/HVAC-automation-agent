"""Interface naar het taalmodel. Workflows praten alleen met dit interface,
zodat we in tests een nep-implementatie gebruiken en het model kunnen wisselen."""

from typing import Protocol

from pydantic import BaseModel, Field

from ..checklists import ChecklistItem


class ExtractedField(BaseModel):
    name: str = Field(description="Naam van het veld, bijv. 'serienummer'")
    value: str


class PhotoAnalysis(BaseModel):
    matched_item_key: str | None = Field(
        description="Key van het checklist-item dat deze foto aantoont, of null als geen enkel item past"
    )
    is_usable: bool = Field(
        description="True als de foto scherp genoeg is en het item duidelijk toont (tekst leesbaar waar nodig)"
    )
    issue: str | None = Field(
        description="Korte uitleg voor de monteur als de foto niet bruikbaar is, anders null"
    )
    extracted: list[ExtractedField] = Field(
        default_factory=list, description="Gegevens afgelezen van de foto (alleen gevraagde velden)"
    )


class MeasurementValue(BaseModel):
    item_key: str
    value: str = Field(description="Waarde met eenheid, zoals de monteur die noemde")


class TextExtraction(BaseModel):
    measurements: list[MeasurementValue] = Field(default_factory=list)
    customer_signed: bool = Field(description="True als de monteur meldt dat de klant akkoord/getekend heeft")
    job_finished_claimed: bool = Field(description="True als de monteur aangeeft klaar te zijn / te vertrekken")
    notes: str | None = Field(description="Overige relevante opmerkingen voor de werkbon, of null")


class LLM(Protocol):
    def analyze_photo(
        self, image: bytes, media_type: str, caption: str | None, items: list[ChecklistItem]
    ) -> PhotoAnalysis: ...

    def extract_text(self, text: str, items: list[ChecklistItem]) -> TextExtraction: ...
