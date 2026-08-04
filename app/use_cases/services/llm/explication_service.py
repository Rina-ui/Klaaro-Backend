import ollama
from typing import Dict, Any, List


class ExplicationService:
    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name

    def generate_explication_complete(
            self,
            rapport_pretraitement: Dict[str, Any],
            charts: List[Dict[str, Any]],
            predictions: Dict[str, Any] = None,
            anomalies: Dict[str, Any] = None,
            metier_contexte: str = "activité générale de l'entreprise"
    ) -> str:
        """
        Analyse les prédictions et anomalies issues de KlaaroMLService et génère
        une explication simple, en langage courant, avec des suggestions d'actions concrètes.
        """

        # 1. Analyse précise des prédictions, en langage simple
        detail_prediction = "Il n'y a pas assez d'informations pour deviner ce qui va se passer ensuite."
        if predictions and predictions.get("status") == "success":
            target = predictions.get("target_column")
            horizon = predictions.get("horizon_jours")
            liste_preds = predictions.get("predictions", [])

            if liste_preds:
                val_actuelle = liste_preds[0].get("valeur", 0)
                val_future = liste_preds[-1].get("valeur", 0)

                if val_actuelle > 0:
                    variation = ((val_future - val_actuelle) / val_actuelle) * 100
                else:
                    variation = 0

                if variation > 0:
                    sens = "ça devrait augmenter"
                elif variation < 0:
                    sens = "ça devrait diminuer"
                else:
                    sens = "ça devrait rester à peu près pareil"

                nom_simple = str(target).replace('_', ' ')

                detail_prediction = (
                    f"On regarde ce qui pourrait se passer pour « {nom_simple} » dans les {horizon} prochains jours.\n"
                    f"En ce moment, ça tourne autour de {val_actuelle:,.2f}.\n"
                    f"Dans {horizon} jours, ça pourrait plutôt être autour de {val_future:,.2f}.\n"
                    f"Autrement dit : {sens}, d'environ {abs(variation):.0f} sur 100."
                )

        # 2. Synthèse des anomalies, en langage simple
        info_anomalies = "Rien d'anormal n'a été repéré dans le fichier."
        if anomalies and anomalies.get("status") == "success":
            nb_anomalies = anomalies.get("anomalies_detectees", 0)
            if nb_anomalies > 0:
                info_anomalies = f"{nb_anomalies} ligne(s) sortent du lot, elles ne ressemblent pas aux autres."

        # 3. Prompt système et consigne détaillée pour Ollama
        system_prompt = (
            "Tu es KLAARO, le conseiller de confiance d'un chef d'entreprise qui n'a aucune formation "
            "en informatique ni en statistiques, mais qui doit prendre de vraies décisions pour son "
            "activité. Tu t'adresses directement à lui, comme un conseiller assis en face de lui.\n\n"
            "Règles strictes :\n"
            "1. Interdiction totale des mots techniques : 'données', 'variable', 'DataFrame', "
            "'imputation', 'scikit-learn', 'corrélation', 'métrique', 'horizon prédictif', 'anomalie'. "
            "Remplace toujours par du langage courant (ex: 'anomalie' -> 'un truc bizarre', "
            "'horizon prédictif' -> 'dans les jours qui viennent').\n"
            "2. Phrases courtes, moins de 15 mots, une idée à la fois.\n"
            "3. Utilise des comparaisons du quotidien pour rendre les choses concrètes, mais garde "
            "toujours le lien avec l'activité de l'entreprise (le chiffre d'affaires, les clients, "
            "le stock, l'équipe, la trésorerie...).\n"
            "4. Jamais de chiffre seul : dis toujours ce que ça veut dire pour la marche de l'entreprise.\n"
            "5. Adresse-toi directement à lui ('vous'), comme un conseiller sérieux qui veut l'aider "
            "à décider, pas comme un copain qui discute. Pas d'introduction du style 'Voici l'analyse' : "
            "va droit au but, avec l'assurance de quelqu'un qui connaît son métier."
        )

        user_prompt = f"""
Voici ce qu'on sait sur : {metier_contexte}

--- CE QUI POURRAIT SE PASSER ENSUITE ---
{detail_prediction}

--- TRUCS BIZARRES REMARQUÉS ---
{info_anomalies}

--- CONSIGNES ---
Rédige une explication simple, adressée directement au chef d'entreprise, structurée comme ceci :

1.  Ce qui pourrait arriver pour votre activité: Expliquez en langage courant ce que ça veut dire,
    concrètement, pour les prochains jours de son entreprise. Pas de chiffres compliqués, juste
    "ça va monter" ou "ça va baisser" et ce que ça change pour ses ventes, ses clients ou sa caisse.
2.  Une opportunité et un point à surveiller : Donnez une bonne nouvelle possible pour l'entreprise
    et un risque possible pour l'entreprise, en une phrase chacun, sans jargon.
3.  Ce que vous pouvez décider maintenant : Proposez 2 à 3 décisions simples et concrètes qu'il
    peut prendre dès aujourd'hui pour son entreprise, comme le ferait un conseiller de confiance.
        """

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response["message"]["content"]

        except Exception as e:
            return (
                f"On n'a pas réussi à préparer l'explication cette fois-ci ({str(e)}). "
                f"Réessayez dans un instant, vos résultats restent disponibles."
            )