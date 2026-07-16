import traceback
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.adapters.dependencies import get_current_user
from app.adapters.schemas.chat_schema import RequeteResponse, RequeteCreate
# Importe tes schémas existants et nos nouveaux schémas IA
from app.adapters.schemas.decision_schema import DecisionResponse, DecisionRequest

from app.infrastructure.database import get_db
from app.infrastructure.repositories.decision_repository_impl import DecisionRepositoryImpl
from app.infrastructure.repositories.chat_repository_impl import ChatRepositoryImpl # À créer pour requete/reponse

# Tes Cas d'Utilisation (Use Cases)
from app.use_cases.services.decision.create_decision import CreateDecision
from app.use_cases.services.decision.find_decisions_by_user import FindDecisionsByUser
from app.use_cases.services.chat.ask_assistant_klaaro import AskAssistantKlaaro # Le nouveau use case

router = APIRouter(
    prefix="/decision",
    tags=["Decision"],
)

@router.post("/demander", response_model=RequeteResponse, status_code=status.HTTP_201_CREATED)
def demander_assistant(
        request: RequeteCreate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    try:
        chat_repo = ChatRepositoryImpl(db)
        use_case = AskAssistantKlaaro(chat_repo)

        return use_case.execute(
            user_id=current_user.id,
            rapport_id=request.rapport_id,
            type_requete=request.type,
            content=request.content,
            chart_data=request.chart_data
        )
    except Exception as e:
        # ICI : On affiche toute la trace de l'erreur dans la console uvicorn !
        print("=== CRASH ASSISTANT DETAILS ===")
        traceback.print_exc()
        print("===============================")
        raise HTTPException(status_code=500, detail=f"Erreur Assistant: {str(e)}")

# 2. ACCEPTER/VALIDER UNE DÉCISION MANUELLEMENT
@router.post("/", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
def create_decision(
        request: DecisionRequest,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    try:
        repo = DecisionRepositoryImpl(db)
        use_case = CreateDecision(repo)
        return use_case.execute(
            content=request.content,
            description=request.description,
            user_id=current_user.id, # Utilise l'ID de l'user connecté plutôt que request.user_id pour la sécurité !
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 3. RÉCUPÉRER TOUTES LES DÉCISIONS D'UN UTILISATEUR
@router.get("/{user_id}", response_model=List[DecisionResponse])
def get_decisions_by_user(
        user_id: str,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    try:
        repo = DecisionRepositoryImpl(db)
        use_case = FindDecisionsByUser(repo)
        return use_case.execute(user_id)
    except Exception as e:
        raise HTTPException(status_code=44, detail=str(e))

# 4. ACCEPTER/VALIDER UNE DÉCISION SPÉCIFIQUE
@router.patch("/{decision_id}/accepter", response_model=DecisionResponse)
def accept_decision(
        decision_id: str,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    try:
        repo = DecisionRepositoryImpl(db)
        # Remplace par ton Use Case de validation de décision
        from app.use_cases.services.decision.accept_decision import AcceptDecision
        use_case = AcceptDecision(repo)
        return use_case.execute(decision_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la validation : {str(e)}")