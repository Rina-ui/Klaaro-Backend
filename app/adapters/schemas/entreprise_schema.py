from datetime import datetime

from pydantic import BaseModel


class EntrepriseRequest(BaseModel):
    name: str
    email: str
    number: str
    location: str

class EntrepriseResponse(BaseModel):
    id: str
    name: str
    email: str
    number: str
    location: str
    creation_date: datetime

    class Config(BaseModel):
        from_attributes = True