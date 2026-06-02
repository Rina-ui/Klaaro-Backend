from app.use_cases.repositories.vulnerabilite_repository import VulnerabiliteRepository

class FindVulnerabilitesByUser:
    def __init__(self, vulnerabilite_repository: VulnerabiliteRepository):
        self.vulnerabilite_repository = vulnerabilite_repository

    def execute(self, user_id: str):
        return self.vulnerabilite_repository.find_vulnerabilite_by_id(user_id)
