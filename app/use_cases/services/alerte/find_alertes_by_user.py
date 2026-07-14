from app.use_cases.repositories.alerte_repository import AlerteRepository

class FindAlertesByUser:
    def __init__(self, alerte_repository: AlerteRepository):
        self.alerte_repository = alerte_repository

    def execute(self, user_id: str):
        return self.alerte_repository.find_by_user_id(user_id)