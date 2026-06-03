from datetime import datetime

from pydantic import BaseModel


class RapportRequest(BaseModel):
    type: str
    content: str
    periode: str

class RapportResponse(BaseModel):
    id: str
    type: str
    content: str
    periode: str
    date_generation: datetime

    class Config(BaseModel):
        from_attribute = True