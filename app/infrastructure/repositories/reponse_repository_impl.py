from sqlalchemy.orm import Session

from app.entities.reponse import Reponse
from app.infrastructure.models.reponse_model import ReponseModel
from app.uses_cases.repositories.reponse_repository import ReponseRepository


class ReponseRepositoryImpl(ReponseRepository):

    def __init__(self, db: Session):
        self.db = db

    def save_response(self, reponse: Reponse):
        model = ReponseModel(**reponse.__dict__)

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return reponse

    def find_by_id(self, rapport_id: str):
        return (
            self.db.query(ReponseModel)
            .filter(ReponseModel.id == rapport_id)
            .first()
        )

    def find_all(self):
        return self.db.query(ReponseModel).all()

    def delete_response(self, rapport_id: str):
        model = (
            self.db.query(ReponseModel)
            .filter(ReponseModel.id == rapport_id)
            .first()
        )

        if model:
            self.db.delete(model)
            self.db.commit()