from datetime import datetime

from pydantic import BaseModel, ConfigDict

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

    model_config = ConfigDict(from_attributes=True)