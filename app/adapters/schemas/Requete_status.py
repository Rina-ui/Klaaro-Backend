from datetime import datetime

from pydantic import BaseModel

from app.entities.enum.typeRequete import TypeRequete


class RequeteRequest(BaseModel):
    type: TypeRequete
    content: str

class RequeteResponse(BaseModel):
    id: str
    type: TypeRequete
    content: str
    send_date: datetime

    class Config(BaseModel):
        from_attribute = True