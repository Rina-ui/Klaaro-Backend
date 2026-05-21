from dataclasses import dataclass
from datetime import datetime

from app.entities.enum.NiveauVul import NiveauVul
from app.entities.enum.Status import Status


@dataclass
class Vulnerabilite:
    id: str
    type: str
    niveau: NiveauVul
    description: str
    status: Status
    date_detected: datetime