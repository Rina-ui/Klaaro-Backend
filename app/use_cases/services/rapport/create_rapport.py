import uuid
from datetime import datetime

from app.entities.enum.typeRapport import TypeRapport
from app.entities.rapport import Rapport
from app.use_cases.repositories.rapport_repository import RapportRepository

class CreateRapport:
    def __init__(self, rapport_repository: RapportRepository):
        self.rapport_repository = rapport_repository

    def execute(self, type: TypeRapport, content: str, periode: str, user_id: str) -> Rapport:
        rapport = Rapport(
            id=str(uuid.uuid4()),
            type=type,
            content=content,
            periode=periode,
            date_generation=datetime.utcnow(),
            user_id=user_id
        )
        return self.rapport_repository.save_rapport(rapport)