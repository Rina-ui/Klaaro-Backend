from sqlalchemy.orm import Session

from app.entities.requete import Requete
from app.infrastructure.models.requete_model import RequeteModel
from app.use_cases.repositories.requete_repository import RequeteRepository


class RequeteRepositoryImpl(RequeteRepository):

    def __init__(self, db: Session):
        self.db = db

    def save_requete(self, requete: Requete):
        model = RequeteModel(**requete.__dict__)

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return requete

    def find_by_id(self, requete_id: str):
        return (
            self.db.query(RequeteModel)
            .filter(RequeteModel.id == requete_id)
            .first()
        )

    def find_all(self):
        return self.db.query(RequeteModel).all()

    def delete_request(self, requete_id: str):
        model = (
            self.db.query(RequeteModel)
            .filter(RequeteModel.id == requete_id)
            .first()
        )

        if model:
            self.db.delete(model)
            self.db.commit()