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
    user_id: str
    upload_date: datetime
    extracted_via_ocr: bool = False