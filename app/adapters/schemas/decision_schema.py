from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.entities.enum.Status import Status


class DecisionRequest(BaseModel):
    content: str
    description: str
    status: Status

class DecisionResponse(BaseModel):
    id: str
    content: str
    description: str
    status: Status
    date: datetime

    model_config = ConfigDict(from_attributes=True)