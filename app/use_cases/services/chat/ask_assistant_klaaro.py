# app/use_cases/services/chat/ask_assistant_klaaro.py

import uuid
from datetime import datetime
from typing import List, Any
from app.entities.enum.typeRequete import TypeRequete
from app.entities.enum.Status import Status
from app.use_cases.services.ml.klaaroIAService import KlaaroAIService


class AskAssistantKlaaro:
    def __init__(self, chat_repository):
        self.chat_repository = chat_repository
        self.ai_service = KlaaroAIService() # Charge le modèle TinyLlama

    def execute(
            self,
            user_id: str,
            rapport_id: str | None,
            type_requete: str,
            content: str,
            chart_data: List[Any] | None = None
    ) -> dict:

        # 1. Récupérer le rapport si l'ID est fourni
        report_content = "{}"
        if rapport_id:
            rapport = self.chat_repository.find_rapport_by_id(rapport_id)
            if not rapport:
                raise ValueError("Rapport introuvable pour l'analyse contextuelle.")
            report_content = rapport.content

        # 2. Formater les données du diagramme (chart_data) en texte lisible pour l'IA
        chart_content = ""
        if chart_data:
            chart_content = "Données du diagramme actuel :\n"
            for point in chart_data:
                if not isinstance(point, dict):
                    continue
                date = point.get("date", "Inconnue")
                historique = point.get("Historique")
                prevision = point.get("Prevision")

                historique_str = f"{historique}" if historique is not None else "Aucune valeur passée"
                prevision_str = f"{prevision}" if prevision is not None else "Aucune prévision"

                chart_content += f"- En date du {date} : Historique = {historique_str}, Prévision = {prevision_str}\n"

        # 3. Préparer les IDs uniques en amont
        requete_id = str(uuid.uuid4())
        reponse_id = str(uuid.uuid4())

        # 4. Combiner le contexte (Rapport + Graphique) pour l'IA
        # On peut passer le texte du graphique directement en l'ajoutant au contexte ou à la requête
        context_global = f"CONTEX_RAPPORT:\n{report_content}\n\n"
        if chart_content:
            context_global += f"DONNEES_DIAGRAMME:\n{chart_content}\n"
            context_global += "CONSIGNE : Interprète et explique très simplement les hausses, baisses ou tendances de ces données de graphique de manière compréhensible."

        # Appeler le modèle local TinyLlama
        ai_result = self.ai_service.generate_decision_and_explanation(
            query_content=content,
            report_content=context_global  # On passe le contexte global enrichi du graphique
        )

        # 5. Préparer les données pour la persistance
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

        # 6. Enregistrer tout d'un coup de manière atomique
        return self.chat_repository.save_conversation(
            requete_data=requete_data,
            reponse_data=reponse_data,
            decisions_data=decisions_list
        )