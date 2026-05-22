from dataclasses import dataclass
from datetime import datetime

from app.entities.enum.NiveauVul import NiveauVul
from app.entities.enum.Status import Status
from app.entities.enum.typeVulnerabilite import TypeVulnerabilite


@dataclass
class Vulnerabilite:
    id: str
    type: TypeVulnerabilite
    niveau: NiveauVul
    description: str
    status: Status
    date_detected: datetime