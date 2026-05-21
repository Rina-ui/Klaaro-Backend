from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    id: str
    name: str
    type: str
    taille: int
    content: str
    upload_date: datetime