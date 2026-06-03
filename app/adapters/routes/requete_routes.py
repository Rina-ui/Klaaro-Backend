from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.adapters.schemas.Requete_status import RequeteResponse, RequeteRequest
from app.infrastructure.database import get_db
from app.infrastructure.repositories.requete_repository_impl import RequeteRepositoryImpl
from app.use_cases.services.requete.create_requete import CreateRequete

router = APIRouter(
    prefix="/request",
    tags=["request"]
)

@router.post("/", response_model=RequeteResponse)
def create_response(request: RequeteRequest, db: Session = Depends(get_db)):
    try:
        repo = RequeteRepositoryImpl(db)
        use_case = CreateRequete(repo)
        return use_case.execute(
            type=request.type,
            content=request.content,
            user_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))