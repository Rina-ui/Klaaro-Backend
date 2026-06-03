from datetime import datetime

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)