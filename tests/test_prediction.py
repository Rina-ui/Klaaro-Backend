import sys
import os

from app.adapters.routes.user_routes import recuperer_dataframe_utilisateur

# Ajout du chemin pour importer tes modules d'application
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.infrastructure.database import engine
from app.infrastructure.models.user_model import UserModel

# Remplace par les vrais imports de ton service de ML et d'alertes s'ils sont différents
# (ex: de app.services.klaaro_ml_service import KlaaroMLService)
# Ici, j'importe un exemple type de ce qu'on a configuré ensemble.
try:
    from app.services.klaaro_ml_service import KlaaroMLService
except ImportError:
    KlaaroMLService = None


def tester_generation_alerte():
    print("=== DÉBUT DU TEST DE PRÉDICTION ===")

    with Session(engine) as db:
        # 1. Récupérer Koffi
        koffi = db.query(UserModel).filter(UserModel.email == "koffi@example.com").first()
        if not koffi:
            print("Erreur : Koffi n'existe pas en base. Lance d'abord le seed !")
            return

        print(f"Utilisateur trouvé : {koffi.firstname} {koffi.lastname}")
        print(f"Option d'alerte : Colonne cible = '{koffi.alerte_colonne_cible}', Fréquence = '{koffi.alerte_frequence}'")

        # 2. Tester la récupération et conversion du rapport en DataFrame
        print("\nTentative de chargement du DataFrame...")
        try:
            df = recuperer_dataframe_utilisateur(koffi.id, db)
            if df is not None and not df.empty:
                print("DataFrame récupéré avec succès !")
                print("Aperçu des données chargées :")
                print(df)
            else:
                print("Avertissement : Le DataFrame récupéré est vide.")
                return
        except Exception as e:
            print(f"Échec lors de la récupération du DataFrame : {e}")
            return

        # 3. Lancement du service de ML
        if KlaaroMLService is None:
            print("\n[Infos] KlaaroMLService n'a pas pu être importé. Vérifie son chemin d'importation.")
            return

        print("\nExécution de la logique de prédiction/détection d'anomalies...")
        try:
            # On simule ce que fait ton scheduler en arrière-plan
            # Modifie l'appel de méthode selon la signature exacte de ton KlaaroMLService
            service = KlaaroMLService(db)

            # Exemple : exécuter l'analyse sur le dataframe de l'utilisateur
            resultat = service.analyser_donnees_utilisateur(
                user_id=koffi.id,
                df=df,
                colonne_cible=koffi.alerte_colonne_cible
            )

            print("Analyse terminée !")
            print(f"Résultat renvoyé : {resultat}")

            # 4. Vérification de l'ajout de l'alerte en BDD
            db.refresh(koffi)
            print(f"\nNombre d'alertes de Koffi en base actuellement : {len(koffi.alertes)}")
            for alerte in koffi.alertes:
                print(f" - [{alerte.type.value if hasattr(alerte.type, 'value') else alerte.type}] {alerte.content} (Gravité: {alerte.niveau_gravite.value if hasattr(alerte.niveau_gravite, 'value') else alerte.niveau_gravite})")

        except Exception as e:
            print(f"Erreur pendant l'exécution du service ML : {e}")

if __name__ == "__main__":
    tester_generation_alerte()