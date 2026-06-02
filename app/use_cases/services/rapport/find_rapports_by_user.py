from app.use_cases.repositories.rapport_repository import RapportRepository

class FindRapportsByUser:
    def __init__(self, rapport_repository: RapportRepository):
        self.rapport_repository = rapport_repository

    def execute(self, user_id: str):
        return self.rapport_repository.find_by_id(user_id)
