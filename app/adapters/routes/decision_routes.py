from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.adapters.dependencies import get_current_user
from app.adapters.schemas.decision_schema import DecisionResponse, DecisionRequest
from app.infrastructure.database import get_db
from app.infrastructure.repositories.decision_repository_impl import DecisionRepositoryImpl
from app.use_cases.services.decision.create_decision import CreateDecision
from app.use_cases.services.decision.find_decisions_by_user import FindDecisionsByUser

router = APIRouter(
     prefix="/decision",
     tags=["Decision"],
 )

@router.get("/", response_model=DecisionResponse)
def create_decision(request: DecisionRequest, db: Session = Depends(get_db),
                    current_user = Depends(get_current_user)):
    try:
        repo = DecisionRepositoryImpl(db)
        use_case = CreateDecision(repo)
        return use_case.execute(
            content=request.content,
            description=request.description,
            user_id=request.user_id,
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{user_id}", response_model=DecisionResponse)
def get_decision(user_id: str, db: Session = Depends(get_db),
                 current_user = Depends(get_current_user)):
    try:
        repo = DecisionRepositoryImpl(db)
        use_case = FindDecisionsByUser(repo)
        return use_case.execute(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))