from datetime import datetime

from pydantic import BaseModel

from app.entities.enum.typeDocument import TypeDocument


class DocumentRequest(BaseModel):
    name: str
    type: TypeDocument
    taille: int
    content: str

class DocumentResponse(BaseModel):
    id: str
    name: str
    type: TypeDocument
    taille: int
    content: str
    upload_date: datetime


    class Config(BaseModel):
        from_attribute = True