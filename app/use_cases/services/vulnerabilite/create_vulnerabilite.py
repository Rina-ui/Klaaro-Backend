import uuid
from datetime import datetime
from app.entities.vulnerabilite import Vulnerabilite
from app.use_cases.repositories.vulnerabilite_repository import VulnerabiliteRepository

class CreateVulnerabilite:
    def __init__(self, vulnerabilite_repository: VulnerabiliteRepository):
        self.vulnerabilite_repository = vulnerabilite_repository

    def execute(self, type: str, niveau: str, description: str, user_id: str) -> Vulnerabilite:
        vulnerabilite = Vulnerabilite(
            id=str(uuid.uuid4()),
            type=type,
            niveau=niveau,
            description=description,
            date_detection=datetime.utcnow(),
            statut="Detected",
            user_id=user_id
        )
        return self.vulnerabilite_repository.save_vulnerabilite(vulnerabilite)
