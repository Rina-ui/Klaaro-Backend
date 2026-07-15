import uuid
from datetime import datetime
from app.entities.enum.typeRequete import TypeRequete
from app.entities.enum.Status import Status
from app.use_cases.services.ml.klaaroIAService import KlaaroAIService


class AskAssistantKlaaro:
    def __init__(self, chat_repository):
        self.chat_repository = chat_repository
        self.ai_service = KlaaroAIService() # Charge le modèle TinyLlama

    def execute(self, user_id: str, rapport_id: str | None, type_requete: TypeRequete, content: str) -> dict:
        # 1. Récupérer le rapport si l'ID est fourni pour donner du contexte à l'IA
        report_content = "{}"
        if rapport_id:
            rapport = self.chat_repository.find_rapport_by_id(rapport_id)
            if not rapport:
                raise ValueError("Rapport introuvable pour l'analyse contextuelle.")
            report_content = rapport.content

        # 2. Préparer les IDs uniques en amont pour lier les entités
        requete_id = str(uuid.uuid4())
        reponse_id = str(uuid.uuid4())

        # 3. Appeler le modèle local TinyLlama
        ai_result = self.ai_service.generate_decision_and_explanation(
            query_content=content,
            report_content=report_content
        )

        # 4. Préparer les données pour la persistance
        requete_data = {
            "id": requete_id,
            "type": type_requete,
            "content": content,
            "send_date": datetime.utcnow(),
            "user_id": user_id,
            "rapport_id": rapport_id
        }

        reponse_data = {
            "id": reponse_id,
            "type": "explication",
            "content": ai_result["explication"],
            "received_at": datetime.utcnow(),
            "received_by": "TINYLLAMA_KLAARO",
            "requete_id": requete_id
        }

        decisions_list = []
        for dec in ai_result.get("decisions", []):
            decisions_list.append({
                "id": str(uuid.uuid4()),
                "content": dec.get("content", "Action suggérée par l'IA"),
                "description": dec.get("description", ""),
                "status": Status.SUGGEREE,
                "date": datetime.utcnow(),
                "user_id": user_id,
                "reponse_id": reponse_id
            })

        # 5. Enregistrer tout d'un coup de manière atomique via le repository
        return self.chat_repository.save_conversation(
            requete_data=requete_data,
            reponse_data=reponse_data,
            decisions_data=decisions_list
        )