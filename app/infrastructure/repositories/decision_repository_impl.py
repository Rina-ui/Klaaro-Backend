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
        pass

    def find_decision_by_id(self, decision_id: str):
        return (
            self.db.query(DecisionModel)
            .filter(DecisionModel.id == decision_id)
            .first()
        )

    def find_all(self):
        return self.db.query(DecisionModel).all()

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
        return (
            self.db.query(DecisionModel)
            .filter(DecisionModel.user_id == user_id)
            .all()
        )