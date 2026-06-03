from datetime import datetime

from pydantic import BaseModel

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

    class Config(BaseModel):
        from_attribute = True