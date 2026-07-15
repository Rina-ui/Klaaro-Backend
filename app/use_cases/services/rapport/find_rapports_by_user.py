from typing import List
from app.entities.rapport import Rapport
from app.use_cases.repositories.rapport_repository import RapportRepository

class FindRapportsByUser:
    def __init__(self, rapport_repository: RapportRepository):
        self.rapport_repository = rapport_repository

    def execute(self, user_id: str) -> List[Rapport]:
        return self.rapport_repository.find_by_user_id(user_id)