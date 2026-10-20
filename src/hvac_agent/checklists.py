"""Checklists per klustype, geladen uit YAML zodat ze per installateur aanpasbaar zijn."""

from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel


class ItemKind(StrEnum):
    PHOTO = "photo"
    MEASUREMENT = "measurement"
    CONFIRMATION = "confirmation"


class ChecklistItem(BaseModel):
    key: str
    kind: ItemKind
    label: str
    extract: list[str] = []


class Checklist(BaseModel):
    job_type: str
    name: str
    items: list[ChecklistItem]

    def item(self, key: str) -> ChecklistItem | None:
        return next((i for i in self.items if i.key == key), None)

    def items_of(self, kind: ItemKind) -> list[ChecklistItem]:
        return [i for i in self.items if i.kind == kind]


def load_checklists(directory: Path) -> dict[str, Checklist]:
    checklists = {}
    for path in sorted(directory.glob("*.yaml")):
        checklist = Checklist.model_validate(yaml.safe_load(path.read_text()))
        checklists[checklist.job_type] = checklist
    return checklists
