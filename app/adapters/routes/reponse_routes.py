from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.adapters.dependencies import get_current_user
from app.adapters.schemas.reponse_status import ReponseResponse, ReponseRequest
from app.infrastructure.database import get_db
from app.infrastructure.repositories.reponse_repository_impl import ReponseRepositoryImpl
from app.use_cases.services.reponse.create_reponse import CreateReponse

router = APIRouter(
    prefix="/response",
    tags=["response"]
)

@router.post("/", response_model=ReponseResponse)
def create_response(request: ReponseRequest, db: Session = Depends(get_db),
                    current_user = Depends(get_current_user)):
    try:
        repo = ReponseRepositoryImpl(db)
        use_case = CreateReponse(repo)
        return use_case.execute(
            type=request.type,
            content=request.content,
            source=request.source,
            requete_id=request.requete_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))