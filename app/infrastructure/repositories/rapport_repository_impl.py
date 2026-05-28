from sqlalchemy.orm import Session

from app.entities.rapport import Rapport
from app.infrastructure.models.rapport_model import RapportModel
from app.uses_cases.repositories.rapport_repository import RapportRepository


class RapportRepositoryImpl(RapportRepository):

    def __init__(self, db: Session):
        self.db = db

    def save_rapport(self, rapport: Rapport):
        model = RapportModel(**rapport.__dict__)

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return rapport

    def update_rapport(self, rapport: Rapport):
        pass

    def find_by_id(self, rapport_id: str):
        return (
            self.db.query(RapportModel)
            .filter(RapportModel.id == rapport_id)
            .first()
        )

    def find_all(self):
        return self.db.query(RapportModel).all()

    def delete_rapport(self, rapport_id: str):
        model = (
            self.db.query(RapportModel)
            .filter(RapportModel.id == rapport_id)
            .first()
        )

        if model:
            self.db.delete(model)
            self.db.commit()