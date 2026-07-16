# app/infrastructure/scheduler.py
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.adapters.routes.user_routes import recuperer_dataframe_utilisateur
from app.infrastructure.database import SessionLocal
from app.infrastructure.models.user_model import UserModel
from app.infrastructure.repositories.alerte_repository_impl import AlerteRepositoryImpl
from app.use_cases.services.ml.klaaro_ml_service import ml_service
from app.use_cases.services.alerte.generer_alerte_prediction import GenererAlertePrediction

# Pour l'instant, on importe le helper vide. On le liera à une vraie source à l'étape suivante.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KlaaroScheduler")

scheduler = BackgroundScheduler()

def verifier_et_generer_alertes_quotidiennes():
    """
    Tâche exécutée pour les utilisateurs ayant choisi 'chaque_jour'.
    """
    logger.info("Début de la vérification des alertes quotidiennes...")
    db: Session = SessionLocal()
    try:
        # 1. Récupérer les utilisateurs abonnés aux alertes quotidiennes
        utilisateurs = db.query(UserModel).filter(
            UserModel.alerte_frequence == "chaque_jour",
            UserModel.alerte_colonne_cible.isnot(None)
        ).all()

        alerte_repo = AlerteRepositoryImpl(db)
        service_alerte = GenererAlertePrediction(alerte_repo)

        for user in utilisateurs:
            try:
                # 2. Récupérer son dataframe
                df_donnees = recuperer_dataframe_utilisateur(user.id, db)
                if df_donnees is not None and not df_donnees.empty:
                    # 3. Lancer la prédiction et sauvegarder l'alerte
                    service_alerte.execute(
                        user_id=user.id,
                        df_donnees=df_donnees,
                        colonne_cible=user.alerte_colonne_cible,
                        n_jours=30
                    )
                    logger.info(f"Alerte quotidienne générée avec succès pour l'utilisateur {user.id}")
                else:
                    logger.warning(f"Pas de données disponibles pour l'utilisateur {user.id}")
            except Exception as e:
                logger.error(f"Erreur lors de la génération d'alerte pour {user.id} : {e}")

    finally:
        db.close()

def verifier_et_generer_alertes_hebdomadaires():
    """
    Tâche exécutée pour les utilisateurs ayant choisi 'toutes_les_semaines'.
    """
    logger.info("Début de la vérification des alertes hebdomadaires...")
    db: Session = SessionLocal()
    try:
        utilisateurs = db.query(UserModel).filter(
            UserModel.alerte_frequence == "toutes_les_semaines",
            UserModel.alerte_colonne_cible.isnot(None)
        ).all()

        alerte_repo = AlerteRepositoryImpl(db)
        service_alerte = GenererAlertePrediction(alerte_repo)

        for user in utilisateurs:
            try:
                df_donnees = recuperer_dataframe_utilisateur(user.id, db)
                if df_donnees is not None and not df_donnees.empty:
                    service_alerte.execute(
                        user_id=user.id,
                        df_donnees=df_donnees,
                        colonne_cible=user.alerte_colonne_cible,
                        n_jours=30
                    )
                    logger.info(f"Alerte hebdomadaire générée avec succès pour l'utilisateur {user.id}")
            except Exception as e:
                logger.error(f"Erreur lors de la génération d'alerte hebdo pour {user.id} : {e}")
    finally:
        db.close()

def start_scheduler():
    """
    Démarre le planificateur de tâches de fond.
    """
    if not scheduler.running:
        # Exécuter la vérification quotidienne tous les jours à minuit
        scheduler.add_job(
            verifier_et_generer_alertes_quotidiennes,
            trigger=CronTrigger(hour=0, minute=0),
            id="alertes_quotidiennes",
            replace_existing=True
        )

        # Exécuter la vérification hebdomadaire tous les lundis à 1h du matin
        scheduler.add_job(
            verifier_et_generer_alertes_hebdomadaires,
            trigger=CronTrigger(day_of_week="mon", hour=1, minute=0),
            id="alertes_hebdomadaires",
            replace_existing=True
        )

        scheduler.start()
        logger.info("Scheduler Klaaro démarré avec succès !")

def shutdown_scheduler():
    """
    Arrête proprement le scheduler à la fermeture de l'application.
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler Klaaro arrêté.")