import uuid
from datetime import datetime
from app.entities.enum.typeAlerte import TypeAlerte
from app.entities.enum.NiveauVul import NiveauVul
from app.entities.alerte import Alerte
from app.use_cases.repositories.alerte_repository import AlerteRepository
from app.use_cases.services.ml.klaaro_ml_service import ml_service
import pandas as pd

class GenererAlertePrediction:
    def __init__(self, alerte_repository: AlerteRepository):
        self.alerte_repository = alerte_repository

    def execute(self, user_id: str, df_donnees: pd.DataFrame, colonne_cible: str, n_jours: int = 30) -> Alerte:
        # 1. On lance la prédiction avec le service ML
        prediction_result = ml_service.predict(df_donnees, target_col=colonne_cible, n_days=n_jours)

        if prediction_result.get("status") == "error":
            raise ValueError(f"Impossible de générer la prédiction : {prediction_result.get('message')}")

        predictions = prediction_result["predictions"]
        historique = prediction_result["historique"]

        # 2. On compare la moyenne des prévisions futures avec celle de l'historique
        valeurs_futures = [p["valeur"] for p in predictions]
        valeurs_passees = [h["valeur"] for h in historique]

        moyenne_passee = sum(valeurs_passees) / len(valeurs_passees) if valeurs_passees else 1
        moyenne_future = sum(valeurs_futures) / len(valeurs_futures) if valeurs_futures else 1

        variation_pct = ((moyenne_future - moyenne_passee) / moyenne_passee) * 100

        # 3. Rédaction du message vulgarisé selon la tendance
        if variation_pct > 5:
            niveau_gravite = NiveauVul.FAIBLE  # Vert / Positif
            titre = "Tendance en Hausse"
            message = f"Les prévisions sur la colonne '{colonne_cible}' indiquent une hausse de {round(variation_pct, 1)}% pour les {n_jours} prochains jours."
        elif variation_pct < -5:
            niveau_gravite = NiveauVul.ELEVE  # Attention
            titre = "Tendance en Baisse"
            message = f"Attention, les prévisions sur la colonne '{colonne_cible}' indiquent une baisse de {round(abs(variation_pct), 1)}% pour les {n_jours} prochains jours."
        else:
            niveau_gravite = NiveauVul.MOYEN
            titre = "Tendance Stable"
            message = f"Les prévisions sur la colonne '{colonne_cible}' restent stables (variation de {round(variation_pct, 1)}%) sur un horizon de {n_jours} jours."

        # 4. On crée et sauvegarde l'alerte
        nouvelle_alerte = Alerte(
            id=str(uuid.uuid4()),
            type=TypeAlerte.PREDICTION,
            content=f"[{titre}] {message}",
            send_date=datetime.now(),
            niveau_gravite=niveau_gravite,
            user_id=user_id
        )

        # CORRECTION ICI : .save() au lieu de .save_alerte()
        self.alerte_repository.save(nouvelle_alerte)
        return nouvelle_alerte