from sqlalchemy.orm import Session

from app.entities.entreprise import Entreprise
from app.infrastructure.models.entreprise_model import EntrepriseModel
from app.uses_cases.repositories.entreprise_repository import EntrepriseRepository


class EntrepriseRepositoryImpl(EntrepriseRepository):

    def __init__(self, db: Session):
        self.db = db

    def save_entreprise(self, entreprise: Entreprise):
        model = EntrepriseModel(**entreprise.__dict__)

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return entreprise

    def update_entreprise(self, entreprise: Entreprise):
        pass

    def find_by_id(self, entreprise_id: str):
        return (
            self.db.query(EntrepriseModel)
            .filter(EntrepriseModel.id == entreprise_id)
            .first()
        )

    def find_all(self):
        return self.db.query(EntrepriseModel).all()

    def delete_entreprise(self, entreprise_id: str):
        model = (
            self.db.query(EntrepriseModel)
            .filter(EntrepriseModel.id == entreprise_id)
            .first()
        )

        if model:
            self.db.delete(model)
            self.db.commit()