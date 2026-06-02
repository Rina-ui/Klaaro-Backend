import uuid
from datetime import datetime
from app.entities.decision import Decision
from app.use_cases.repositories.decision_repository import DecisionRepository

class CreateDecision:
    def __init__(self, decision_repository: DecisionRepository):
        self.decision_repository = decision_repository

    def execute(self, content: str, description: str, user_id: str) -> Decision:
        decision = Decision(
            id=str(uuid.uuid4()),
            content=content,
            description=description,
            date=datetime.utcnow(),
            statut="pending",
            user_id=user_id
        )
        return self.decision_repository.save_decision(decision)
