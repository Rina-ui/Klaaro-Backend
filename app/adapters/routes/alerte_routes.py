from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.adapters.schemas.alerte_schema import AlerteResponse, AlerteRequest
from app.infrastructure.database import get_db
from app.infrastructure.repositories.alerte_repository_impl import AlerteRepositoryImpl
from app.use_cases.services.alerte.create_alerte import CreateAlerte
from app.use_cases.services.alerte.find_alertes_by_user import FindAlertesByUser

router = APIRouter(
    prefix="/alert",
    tags=["alert"],
)

@router.post("/", response_model=AlerteResponse)
def create_alerte(request: AlerteRequest, db: Session = Depends(get_db)):
    try:
        repo = AlerteRepositoryImpl(db)
        use_case = CreateAlerte(repo)
        return use_case.execute(
            type=type,
            content=request.content,
            niveau_gravite=request.niveau_gravite,
            user_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/alerts/{id}", response_model=AlerteResponse)
def get_alert(user_id: str, db: Session = Depends(get_db)):
    try:
        repo = AlerteRepositoryImpl(db)
        use_case = FindAlertesByUser(repo)
        return use_case.execute(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))