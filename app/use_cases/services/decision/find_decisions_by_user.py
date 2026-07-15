from typing import List
from app.entities.decision import Decision
from app.use_cases.repositories.decision_repository import DecisionRepository

class FindDecisionsByUser:
    def __init__(self, decision_repository: DecisionRepository):
        self.decision_repository = decision_repository

    def execute(self, user_id: str) -> List[Decision]:
        return self.decision_repository.find_by_user_id(user_id)