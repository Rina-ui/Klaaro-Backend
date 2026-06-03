from pydantic import BaseModel
from datetime import datetime
from app.entities.enum.typeAlerte import TypeAlerte
from app.entities.enum.NiveauVul import NiveauVul

class AlerteRequest(BaseModel):
    type: TypeAlerte
    content: str
    niveau_gravite: NiveauVul
    user_id: str

class AlerteResponse(BaseModel):
    id: str
    type: TypeAlerte
    content: str
    send_date: datetime
    niveau_gravite: NiveauVul
    user_id: str

    class Config:
        from_attribute = True