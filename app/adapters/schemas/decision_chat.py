from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from app.entities.enum.typeRequete import TypeRequete
from app.entities.enum.Status import Status

# --- SCHÉMAS POUR LES DÉCISIONS ---
class DecisionBase(BaseModel):
    content: str = Field(..., example="Ajustement de stock de sécurité")
    description: str = Field(..., example="Commander 150 unités de l'article X pour éviter une rupture sous 10 jours.")
    status: Status = Field(default=Status.SUGGEREE)

class DecisionCreate(DecisionBase):
    pass

class DecisionResponse(DecisionBase):
    id: str
    date: datetime
    user_id: str
    reponse_id: str

    class Config:
        from_attributes = True


# --- SCHÉMAS POUR LA RÉPONSE IA ---
class ReponseBase(BaseModel):
    type: str = Field(default="explication")
    content: str = Field(..., example="Voici l'analyse vulgarisée de vos données...")
    received_by: str = Field(default="TINYLLAMA_KLAARO")

class ReponseResponse(ReponseBase):
    id: str
    received_at: datetime
    requete_id: str
    decisions: List[DecisionResponse] = [] # Inclut directement les fiches d'actions liées

    class Config:
        from_attributes = True


# --- SCHÉMAS POUR LA REQUÊTE UTILISATEUR ---
class RequeteCreate(BaseModel):
    type: TypeRequete = Field(..., example=TypeRequete.ANALYSE)
    content: str = Field(..., example="Pourquoi mes ventes ont baissé ce mois-ci ?")
    rapport_id: Optional[str] = Field(None, example="rapport-uuid-123")

class RequeteResponse(BaseModel):
    id: str
    type: TypeRequete
    content: str
    send_date: datetime
    user_id: str
    rapport_id: Optional[str]
    reponse: Optional[ReponseResponse] = None # Inclut directement la réponse de l'IA si elle a été générée

    class Config:
        from_attributes = True