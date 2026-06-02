from sqlalchemy.orm import Session

from app.entities.reponse import Reponse
from app.infrastructure.models.reponse_model import ReponseModel
from app.use_cases.repositories.reponse_repository import ReponseRepository


class ReponseRepositoryImpl(ReponseRepository):

    def __init__(self, db: Session):
        self.db = db

    def save_response(self, reponse: Reponse):
        model = ReponseModel(**reponse.__dict__)

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return reponse

    def find_by_id(self, reponse_id: str):
        return (
            self.db.query(ReponseModel)
            .filter(ReponseModel.id == reponse_id)
            .first()
        )

    def find_all(self):
        return self.db.query(ReponseModel).all()

    def delete_response(self, reponse_id: str):
        model = (
            self.db.query(ReponseModel)
            .filter(ReponseModel.id == reponse_id)
            .first()
        )

        if model:
            self.db.delete(model)
            self.db.commit()