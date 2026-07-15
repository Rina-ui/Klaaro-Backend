from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.adapters.dependencies import get_current_user
from app.adapters.schemas.rapport_schema import RapportResponse, RapportRequest
from app.infrastructure.database import get_db
from app.infrastructure.repositories.rapport_repository_impl import RapportRepositoryImpl
from app.use_cases.services.rapport.create_rapport import CreateRapport
from app.use_cases.services.rapport.find_rapports_by_user import FindRapportsByUser

router = APIRouter(
    prefix="/rapports",
    tags=["Rapports"]
)

# 1. CRÉATION D'UN RAPPORT
@router.post("/", response_model=RapportResponse, status_code=status.HTTP_201_CREATED)
def create_rapport(
        request: RapportRequest,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    try:
        repo = RapportRepositoryImpl(db)
        use_case = CreateRapport(repo)
        return use_case.execute(
            type=request.type,
            content=request.content,
            periode=request.periode,
            user_id=current_user.id,
        )
    except Exception as e:
        # Ajoute ce print pour voir l'erreur exacte dans ta console de terminal !
        import traceback
        print("--- ERREUR DANS CREATE_RAPPORT ---")
        traceback.print_exc()
        print("---------------------------------")
        raise HTTPException(status_code=400, detail=str(e))

# 2. RÉCUPÉRATION DES RAPPORTS DE L'UTILISATEUR CONNECTÉ
@router.get("/me", response_model=List[RapportResponse])
def get_my_rapports(
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        repo = RapportRepositoryImpl(db)
        use_case = FindRapportsByUser(repo)
        rapports = use_case.execute(current_user.id)
        return rapports or []
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))