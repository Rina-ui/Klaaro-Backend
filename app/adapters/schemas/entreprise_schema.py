from datetime import datetime

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)