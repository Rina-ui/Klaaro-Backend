import inspect
from app.entities.decision import Decision
from app.infrastructure.models.decision_model import DecisionModel
from app.use_cases.repositories.decision_repository import DecisionRepository
from sqlalchemy.orm import Session


class DecisionRepositoryImpl(DecisionRepository):

    def __init__(self, db: Session) -> None:
        self.db = db
        # On récupère dynamiquement les paramètres acceptés par l'entité Decision
        self._decision_fields = set(inspect.signature(Decision.__init__).parameters.keys()) - {'self'}

    def _to_entity(self, model: DecisionModel) -> Decision:
        """Convertit un modèle DB en entité pure en ne gardant que les champs compatibles."""
        if not model:
            return None
        # 1. On nettoie l'état SQLAlchemy
        clean_dict = {k: v for k, v in model.__dict__.items() if not k.startswith('_')}
        # 2. On ne garde que les champs que l'entité Decision accepte dans son __init__
        entity_dict = {k: v for k, v in clean_dict.items() if k in self._decision_fields}
        return Decision(**entity_dict)

    def save_decision(self, decision: Decision):
        model = DecisionModel(**decision.__dict__)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return decision

    def update_decision(self, decision: Decision):
        model = (
            self.db.query(DecisionModel)
            .filter(DecisionModel.id == decision.id)
            .first()
        )
        if model:
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
        return self._to_to_entity(model) if model else None

    def find_all(self):
        models = self.db.query(DecisionModel).all()
        return [self._to_entity(m) for m in models]

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
        return [self._to_entity(m) for m in models]