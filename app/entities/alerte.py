from dataclasses import dataclass
from datetime import datetime

from app.entities.enum.NiveauVul import NiveauVul
from app.entities.enum.typeAlerte import TypeAlerte


@dataclass
class Alerte:
    id: str
    type: TypeAlerte
    content: str
    send_date: datetime
    niveau_gravity: NiveauVul
