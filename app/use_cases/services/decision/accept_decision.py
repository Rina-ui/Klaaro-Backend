from app.use_cases.repositories.decision_repository import DecisionRepository
# Importe ton Enum Status depuis le bon dossier (ex: app.entities.decision ou app.adapters.schemas)
from app.entities.decision import Status

class AcceptDecision:
    def __init__(self, repository: DecisionRepository):
        self.repository = repository

    def execute(self, decision_id: str):
        # 1. On récupère la décision
        decision = self.repository.find_decision_by_id(decision_id)
        if not decision:
            raise ValueError("Décision introuvable")

        # 2. On passe le statut à "approuvee" (qui correspond à ta valeur "approuvee")
        decision.status = Status.APPROUVEE.value

        # 3. On sauvegarde la modification en base via le Repository corrigé
        return self.repository.update_decision(decision)