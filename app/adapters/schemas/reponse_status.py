from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReponseRequest(BaseModel):
    type: str
    content: str
    received_by: str

class ReponseResponse(BaseModel):
    id: str
    type: str
    content: str
    received_at: datetime
    received_by: str

    model_config = ConfigDict(from_attributes=True)