from dataclasses import dataclass
from datetime import datetime

from app.entities.enum.typeDocument import TypeDocument


@dataclass
class Document:
    id: str
    name: str
    type: TypeDocument
    taille: int
    content: str
    upload_date: datetime