from dataclasses import dataclass
from datetime import datetime


@dataclass
class Alerte:
    id: str
    type: str
    content: str
    send_date: datetime
    niveau_gravite: str
