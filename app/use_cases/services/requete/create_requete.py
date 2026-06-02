import uuid
from datetime import datetime
from app.entities.requete import Requete
from app.use_cases.repositories.requete_repository import RequeteRepository

class CreateRequete:
    def __init__(self, requete_repository: RequeteRepository):
        self.requete_repository = requete_repository

    def execute(self, type: str, content: str, user_id: str) -> Requete:
        requete = Requete(
            id=str(uuid.uuid4()),
            type=type,
            content=content,
            send_date=datetime.utcnow(),
            user_id=user_id
        )
        return self.requete_repository.save_requete(requete)
