from typing import List, Optional
from sqlalchemy.orm import Session

from app.entities.alerte import Alerte
from app.infrastructure.models.alerte_model import AlerteModel
from app.use_cases.repositories.alerte_repository import AlerteRepository


class AlerteRepositoryImpl(AlerteRepository):

    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, alerte: Alerte) -> Alerte:
        # 1. On filtre proprement le dictionnaire pour éviter les clés système cachées
        data = {k: v for k, v in alerte.__dict__.items() if not k.startswith('_')}

        model = AlerteModel(**data)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return alerte

    def update_alert(self, alerte: Alerte):
        # Si tu as besoin de mettre à jour une alerte plus tard
        model = self.db.query(AlerteModel).filter(AlerteModel.id == alerte.id).first()
        if model:
            model.content = alerte.content
            model.niveau_gravite = alerte.niveau_gravite
            # Ajoute d'autres champs à mettre à jour si nécessaire
            self.db.commit()
        return alerte

    def find_by_id(self, alerte_id: str) -> Optional[Alerte]:
        model = (
            self.db.query(AlerteModel)
            .filter(AlerteModel.id == alerte_id)
            .first()
        )
        if not model:
            return None

        # 2. On transforme le modèle SQL en Entité pure avant de le renvoyer
        return Alerte(
            id=model.id,
            type=model.type,
            content=model.content,
            send_date=model.send_date,
            niveau_gravite=model.niveau_gravite,
            user_id=model.user_id
        )

    def find_all(self) -> List[Alerte]:
        models = self.db.query(AlerteModel).all()
        # On transforme toute la liste en Entités
        return [
            Alerte(
                id=m.id,
                type=m.type,
                content=m.content,
                send_date=m.send_date,
                niveau_gravite=m.niveau_gravite,
                user_id=m.user_id
            ) for m in models
        ]

    def delete(self, alerte_id: str) -> None:
        model = self.db.query(AlerteModel).filter(AlerteModel.id == alerte_id).first()
        if model:
            self.db.delete(model)
            self.db.commit()

    def find_by_user_id(self, user_id: str) -> List[Alerte]:
        models = (
            self.db.query(AlerteModel)
            .filter(AlerteModel.user_id == user_id)
            .order_by(AlerteModel.send_date.desc())
            .all()
        )
        # On transforme également ici
        return [
            Alerte(
                id=m.id,
                type=m.type,
                content=m.content,
                send_date=m.send_date,
                niveau_gravite=m.niveau_gravite,
                user_id=m.user_id
            ) for m in models
        ]