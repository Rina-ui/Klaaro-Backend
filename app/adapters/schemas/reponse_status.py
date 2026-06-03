from datetime import datetime

from pydantic import BaseModel


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

    class Config(BaseModel):
        from_attribute = True