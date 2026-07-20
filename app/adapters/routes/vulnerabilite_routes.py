from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.adapters.dependencies import get_current_user
from app.adapters.schemas.vulnerabilite_status import VulnerabiliteResponse, VulnerabiliteRequest
from app.infrastructure.database import get_db
from app.infrastructure.repositories.vulnerabilite_repository_impl import VulnerabiliteRepositoryImpl
from app.use_cases.services.vulnerabilite.create_vulnerabilite import CreateVulnerabilite
from app.use_cases.services.vulnerabilite.find_vulnerabilites_by_user import FindVulnerabilitesByUser

router = APIRouter(
    prefix="/vulnerability",
    tags=["vulnerability"]
)

@router.post("/", response_model=VulnerabiliteResponse)
def create_vulnerabilite(
        request: VulnerabiliteRequest,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    try:
        repo = VulnerabiliteRepositoryImpl(db)
        use_case = CreateVulnerabilite(repo)
        return use_case.execute(
            type=request.TypeVulnerabilite,
            niveau=request.NiveauVul,
            description=request.description,
            user_id=request.user_id,
        )
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))

# --- CORRECTION ICI : Utilisation de List[VulnerabiliteResponse] ---
@router.get("/{user_id}", response_model=List[VulnerabiliteResponse])
def get_vulnerabilite(
        user_id: str,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    try:
        repo = VulnerabiliteRepositoryImpl(db)
        use_case = FindVulnerabilitesByUser(repo)
        result = use_case.execute(user_id)

        # Si le résultat est None, renvoyer une liste vide au lieu de faire planter FastAPI
        if result is None:
            return []

        # Si le cas d'usage renvoie un objet unique, l'encapsuler dans une liste
        if not isinstance(result, list):
            return [result]

        return result
    except Exception as err:
        # En cas d'erreur ou d'absence d'élément, retourner une liste vide
        return []