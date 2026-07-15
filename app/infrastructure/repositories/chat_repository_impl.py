from sqlalchemy.orm import Session

from app.infrastructure.models.decision_model import DecisionModel
from app.infrastructure.models.rapport_model import RapportModel
from app.infrastructure.models.reponse_model import ReponseModel
from app.infrastructure.models.requete_model import RequeteModel


class ChatRepositoryImpl:
    def __init__(self, db: Session):
        self.db = db

    def find_rapport_by_id(self, rapport_id: str) -> RapportModel | None:
        return self.db.query(RapportModel).filter(RapportModel.id == rapport_id).first()

    def save_conversation(self, requete_data: dict, reponse_data: dict, decisions_data: list) -> RequeteModel:
        try:
            # 1. Création de l'objet Requête
            nouvelle_requete = RequeteModel(**requete_data)
            self.db.add(nouvelle_requete)
            self.db.flush() # Assigne l'ID en base sans commiter

            # 2. Création de l'objet Réponse
            nouvelle_reponse = ReponseModel(**reponse_data)
            self.db.add(nouvelle_reponse)
            self.db.flush()

            # 3. Création des Décisions associées
            for dec_data in decisions_data:
                nouvelle_decision = DecisionModel(**dec_data)
                self.db.add(nouvelle_decision)

            # 4. Validation finale
            self.db.commit()
            self.db.refresh(nouvelle_requete)

            return nouvelle_requete

        except Exception as e:
            self.db.rollback()
            raise e