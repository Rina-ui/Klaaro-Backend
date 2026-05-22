from dataclasses import dataclass
from datetime import datetime


@dataclass
class Requete:
    id: str
    type: str
    content: str
    send_date: datetime