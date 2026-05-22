from dataclasses import dataclass
from datetime import datetime

from app.entities.enum.typeRequete import TypeRequete


@dataclass
class Requete:
    id: str
    type: TypeRequete
    content: str
    send_date: datetime