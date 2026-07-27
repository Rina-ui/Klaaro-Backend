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
        Analyse l'ensemble des résultats de KlaaroMLService (nettoyage, graphiques,
        anomalies et prédictions) et génère une explication décisionnelle avec des
        suggestions d'actions stratégiques.
        """

        # 1. Synthèse des graphiques générés
        resume_charts = []
        for chart in charts:
            title = chart.get('title', 'Graphique')
            explanation = chart.get('explanation', '')
            resume_charts.append(f"- **{title}** : {explanation}")

        chaine_charts = "\n".join(resume_charts) if resume_charts else "Aucun graphique disponible."

        # 2. Analyse précise des prédictions
        detail_prediction = "Aucune prédiction disponible."
        if predictions and predictions.get("status") == "success":
            target = predictions.get("target_column")
            horizon = predictions.get("horizon_jours")
            liste_preds = predictions.get("predictions", [])

            if liste_preds:
                val_actuelle = liste_preds[0].get("valeur", 0)
                val_future = liste_preds[-1].get("valeur", 0)

                # Calcul de la variation en %
                if val_actuelle > 0:
                    variation = ((val_future - val_actuelle) / val_actuelle) * 100
                else:
                    variation = 0

                sens = "hausse" if variation > 0 else "baisse" if variation < 0 else "stabilité"

                detail_prediction = (
                    f"Variable analysée : '{target}'\n"
                    f"- Horizon prédictif : {horizon} jours\n"
                    f"- Valeur de départ estimée : {val_actuelle:,.2f}\n"
                    f"- Valeur projetée dans {horizon} jours : {val_future:,.2f}\n"
                    f"- Tendances observées : {sens} globale estimée à {abs(variation):.1f}%."
                )

        # 3. Synthèse des anomalies
        info_anomalies = "Aucune anomalie détectée."
        if anomalies and anomalies.get("status") == "success":
            nb_anomalies = anomalies.get("anomalies_detectees", 0)
            if nb_anomalies > 0:
                info_anomalies = f"{nb_anomalies} ligne(s) ont été identifiées comme des comportements ou valeurs atypiques."

        # 4. Prompt système et consigne détaillée pour Ollama
        system_prompt = (
            "Tu es KLAARO, la plateforme intelligente d'aide à la décision. "
            "Ton rôle est d'analyser les données traitées et les prédictions fournies, "
            "puis d'expliquer ce qu'elles signifient pour la gestion de l'entreprise. "
            "Ne parle pas de termes trop techniques (comme 'DataFrames', 'imputation', 'scikit-learn'). "
            "Adopte une posture de conseiller stratégique simple, direct et axé sur l'action."
        )

        user_prompt = f"""
Voici le rapport complet issu des traitements KLAARO ({metier_contexte}) :

--- RÉSULTATS DES DONNÉES ET TENDANCES ---
{chaine_charts}

--- SÉCURITÉ ET ANOMALIES ---
- Anomalies : {info_anomalies}

--- PRÉVISIONS DE MACHINE LEARNING ---
{detail_prediction}

--- CONSIGNES ---
Rédige une synthèse décisionnelle structurée de la manière suivante :

1.  **Ce qu'il faut retenir** : Résume en 2-3 phrases les enseignements clés tirés des données.
2.  **Explication de la Prédiction** : Explique ce que signifie concrètement la tendance future ({detail_prediction}) pour l'activité dans les prochains jours.
3.  **Risques & Opportunités** : Liste 1 opportunité et 1 risque majeur liés à cette prédiction.
4.  **Suggestions de Décisions Concrètes** : Propose 2 à 3 actions concrètes et stratégiques immédiates à prendre par la direction ou l'équipe opérationnelle.
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
                f"L'analyse des données est effectuée avec succès, mais la génération "
                f"de la synthèse textuelle Ollama n'a pas pu aboutir ({str(e)})."
            )