from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from app.entities.enum.typeRequete import TypeRequete
from app.entities.enum.Status import Status

# --- SCHÉMA DES DÉCISIONS INCLUSES DANS LA RÉPONSE ---
class DecisionEmbeddedResponse(BaseModel):
    id: str
    content: str
    description: str
    status: Status
    date: datetime
    user_id: str

    class Config:
        from_attributes = True


# --- SCHÉMA DE LA RÉPONSE DE L'IA ---
class ReponseResponse(BaseModel):
    id: str
    type: str
    content: str  # C'est l'explication vulgarisée générée par TinyLlama
    received_at: datetime
    received_by: str
    requete_id: str
    decisions: List[DecisionEmbeddedResponse] = [] # Les actions concrètes extraites de l'explication

    class Config:
        from_attributes = True


# --- SCHÉMA DE CRÉATION DE LA REQUÊTE ---
class RequeteCreate(BaseModel):
    type: TypeRequete = Field(..., example=TypeRequete.ANALYSE)
    content: str = Field(..., example="Explique-moi pourquoi l'âge moyen de mes employés pose problème.")
    rapport_id: Optional[str] = Field(None, example="rapport-uuid-123")


# --- SCHÉMA DE RETOUR COMPLET (Requête + Réponse IA + Décisions) ---
class RequeteResponse(BaseModel):
    id: str
    type: TypeRequete
    content: str
    send_date: datetime
    user_id: str
    rapport_id: Optional[str]
    reponse: Optional[ReponseResponse] = None # Contient l'explication et ses décisions associées

    class Config:
        from_attributes = True