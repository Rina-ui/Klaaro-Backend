from sqlalchemy.orm import Session

from app.entities.vulnerabilite import Vulnerabilite
from app.infrastructure.models.vulnerabilite_model import VulnerabiliteModel
from app.uses_cases.repositories.vulnerabilite_repository import VulnerabiliteRepository


class VulnerabiliteRepositoryImpl(VulnerabiliteRepository):

    def __init__(self, db: Session):
        self.db = db

    def save_vulnerabilite(self, vulnerabilite: Vulnerabilite):
        mddel = VulnerabiliteModel(**vulnerabilite.__dict__)

        self.db.add(mddel)
        self.db.commit()
        self.db.refresh(vulnerabilite)

        return vulnerabilite

    def find_vulnerabilite_by_id(self, vulnerabilite_id: str):
        return (
            self.db.query(VulnerabiliteModel)
            .filter(VulnerabiliteModel.id == vulnerabilite_id)
            .first()
        )

    def find_all(self) :
        return self.db.query(VulnerabiliteModel).all()


    def delete_vulnerabilite_by_id(self, vulnerabilite_id: str):
        model = (
            self.db.query(VulnerabiliteModel)
            .filter(VulnerabiliteModel.id == vulnerabilite_id)
            .first()
        )

        if model:
            self.db.delete(model)
            self.db.commit()