from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.entities.enum.NiveauVul import NiveauVul
from app.entities.enum.Status import Status
from app.entities.enum.typeVulnerabilite import TypeVulnerabilite


class VulnerabiliteRequest(BaseModel):
    type: TypeVulnerabilite
    niveau: NiveauVul
    description: str
    status: Status

class VulnerabiliteResponse(BaseModel):
    id: str
    type: TypeVulnerabilite
    niveau: NiveauVul
    description: str
    status: Status
    date_detected: datetime

    model_config = ConfigDict(from_attributes=True)