import uuid
from datetime import datetime
from app.entities.alerte import Alerte
from app.use_cases.repositories.alerte_repository import AlerteRepository

class CreateAlerte:
    def __init__(self, alerte_repository: AlerteRepository):
        self.alerte_repository = alerte_repository

    def execute(self, type: str, content: str, niveau_gravite: str, user_id: str) -> Alerte:
        alerte = Alerte(
            id=str(uuid.uuid4()),
            type=type,
            content=content,
            send_date=datetime.utcnow(),
            niveau_gravite=niveau_gravite,
            user_id=user_id
        )
        return self.alerte_repository.save(alerte)
