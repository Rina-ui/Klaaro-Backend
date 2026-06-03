from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.entities.enum.typeRequete import TypeRequete


class RequeteRequest(BaseModel):
    type: TypeRequete
    content: str

class RequeteResponse(BaseModel):
    id: str
    type: TypeRequete
    content: str
    send_date: datetime

    model_config = ConfigDict(from_attributes=True)