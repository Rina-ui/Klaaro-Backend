from app.entities.decision import Decision
from app.infrastructure.models.decision_model import DecisionModel
from app.use_cases.repositories.decision_repository import DecisionRepository
from sqlalchemy.orm import Session


class DecisionRepositoryImpl(DecisionRepository):

    def __init__(self, db: Session) -> None:
        self.db = db

    def save_decision(self, decision: Decision):
        model = DecisionModel(**decision.__dict__)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return decision

    def update_decision(self, decision: Decision):
        # On récupère le modèle existant en base
        model = (
            self.db.query(DecisionModel)
            .filter(DecisionModel.id == decision.id)
            .first()
        )
        if model:
            # On met à jour les champs du modèle avec les valeurs de l'entité
            for key, value in decision.__dict__.items():
                setattr(model, key, value)

            self.db.commit()
            self.db.refresh(model)
        return decision

    def find_decision_by_id(self, decision_id: str):
        model = (
            self.db.query(DecisionModel)
            .filter(DecisionModel.id == decision_id)
            .first()
        )
        if not model:
            return None
        # On reconstruit l'entité métier à partir du modèle ORM
        return Decision(**model.__dict__)

    def find_all(self):
        models = self.db.query(DecisionModel).all()
        return [Decision(**m.__dict__) for m in models]

    def delete_decision(self, decision_id: str):
        model = (
            self.db.query(DecisionModel)
            .filter(DecisionModel.id == decision_id)
            .first()
        )
        if model:
            self.db.delete(model)
            self.db.commit()

    def find_by_user_id(self, user_id: str):
        models = (
            self.db.query(DecisionModel)
            .filter(DecisionModel.user_id == user_id)
            .all()
        )
        return [Decision(**m.__dict__) for m in models]