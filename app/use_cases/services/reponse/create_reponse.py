import uuid
from datetime import datetime
from app.entities.reponse import Reponse
from app.use_cases.repositories.reponse_repository import ReponseRepository

class CreateReponse:
    def __init__(self, reponse_repository: ReponseRepository):
        self.reponse_repository = reponse_repository

    def execute(self, type: str, content: str, source: str, requete_id: str) -> Reponse:
        reponse = Reponse(
            id=str(uuid.uuid4()),
            type=type,
            content=content,
            received_at=datetime.utcnow(),
            received_by=source,
            requete_id=requete_id
        )
        return self.reponse_repository.save_response(reponse)
