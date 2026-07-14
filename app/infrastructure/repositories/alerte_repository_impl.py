from app.entities.alerte import Alerte
from app.infrastructure.models.alerte_model import AlerteModel
from app.use_cases.repositories.alerte_repository import AlerteRepository
from sqlalchemy.orm import Session


class AlerteRepositoryImpl(AlerteRepository):

    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, alerte: Alerte):
        model = AlerteModel(**alerte.__dict__)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return alerte

    def update_alert(self, alerte: Alerte):
        pass

    def find_by_id(self, alerte_id: str):
        return (
            self.db.query(AlerteModel)
            .filter(AlerteModel.id == alerte_id)
            .first()
        )

    def find_all(self):
        return self.db.query(AlerteModel).all()

    def delete(self, alerte_id: str) -> None:
        model = self.db.query(AlerteModel).filter(AlerteModel.id == alerte_id).first()
        self.db.delete(model)
        self.db.commit()

    def find_by_user_id(self, user_id: str):
        return (
            self.db.query(AlerteModel)
            .filter(AlerteModel.user_id == user_id)
            .order_by(AlerteModel.send_date.desc())
            .all()
        )