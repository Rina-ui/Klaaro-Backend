# seed.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import uuid
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.infrastructure.database import engine, Base
from app.infrastructure.models.user_model import UserModel
from app.infrastructure.models.entreprise_model import EntrepriseModel
from app.infrastructure.models.document_model import DocumentModel
from app.infrastructure.models.alerte_model import AlerteModel
from app.infrastructure.models.rapport_model import RapportModel
from app.infrastructure.models.requete_model import RequeteModel
from app.infrastructure.models.reponse_model import ReponseModel
from app.infrastructure.models.vulnerabilite_model import VulnerabiliteModel
from app.infrastructure.models.decision_model import DecisionModel
from app.infrastructure.models.database_model import DatabaseConnectionModel


# Importation de TOUTES tes Enums
from app.entities.enum.typeRapport import TypeRapport
from app.entities.enum.role import Role
from app.entities.enum.account_type import AccountType
from app.entities.enum.typeAlerte import TypeAlerte
from app.entities.enum.NiveauVul import NiveauVul
from app.entities.enum.Status import Status
from app.entities.enum.typeDocument import TypeDocument
from app.entities.enum.typeRequete import TypeRequete
from app.entities.enum.typeVulnerabilite import TypeVulnerabilite
from app.entities.enum.typeReponse import TypeReponse

# AJOUT de ton enum DBType
from app.entities.enum.dbType import DBType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed():
    print("Seeding de la base de données...")

    print("Mise à jour de la structure des tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Structure de la base de données réinitialisée !")

    with Session(engine) as db:

        # Nettoyer les tables dans le bon ordre (les clés étrangères d'abord)
        db.query(DecisionModel).delete()
        db.query(VulnerabiliteModel).delete()
        db.query(ReponseModel).delete()
        db.query(RequeteModel).delete()
        db.query(RapportModel).delete()
        db.query(AlerteModel).delete()
        db.query(DocumentModel).delete()
        db.query(DatabaseConnectionModel).delete()  # AJOUT du nettoyage
        db.query(UserModel).delete()
        db.query(EntrepriseModel).delete()
        db.commit()
        print("Tables nettoyées")

        # ===== ENTREPRISES =====
        entreprise1 = EntrepriseModel(
            id=str(uuid.uuid4()),
            name="Boutique Adawlato",
            email="adawlato@gmail.com",
            number="+22890112233",
            location="Lomé, Togo",
            creation_date=datetime(2022, 3, 15)
        )
        entreprise2 = EntrepriseModel(
            id=str(uuid.uuid4()),
            name="Restaurant Le Bénin",
            email="restaurant.benin@gmail.com",
            number="+22891445566",
            location="Lomé, Togo",
            creation_date=datetime(2021, 7, 10)
        )
        db.add_all([entreprise1, entreprise2])
        db.commit()
        print("Entreprises créées")

        # ===== USERS =====
        # Les champs 'alerte_frequence' et 'alerte_colonne_cible' ont été ajoutés explicitement
        user1 = UserModel(
            id=str(uuid.uuid4()),
            firstname="Koffi",
            lastname="Mensah",
            email="koffi@example.com",
            password=pwd_context.hash("password123"),
            profession="Gérant",
            role=Role.USER.value,
            account_type=AccountType.ENTREPRISE,
            entreprise_id=entreprise1.id,
            alerte_frequence="chaque_jour",
            alerte_colonne_cible="ventes"
        )
        user2 = UserModel(
            id=str(uuid.uuid4()),
            firstname="Ama",
            lastname="Koffi",
            email="ama@example.com",
            password=pwd_context.hash("password123"),
            profession="Data Scientist",
            role=Role.USER.value,
            account_type=AccountType.INDIVIDUAL,
            entreprise_id=None,
            alerte_frequence="toutes_les_semaines",
            alerte_colonne_cible="montant"
        )
        user_admin = UserModel(
            id=str(uuid.uuid4()),
            firstname="Admin",
            lastname="Klaaro",
            email="admin@klaaro.com",
            password=pwd_context.hash("admin123"),
            profession="Administrateur",
            role=Role.ADMIN.value,
            account_type=AccountType.INDIVIDUAL,
            entreprise_id=None,
            alerte_frequence="chaque_jour",
            alerte_colonne_cible="ventes"
        )
        db.add_all([user1, user2, user_admin])
        db.commit()
        print("Users créés")

        # ===== CONNEXIONS BASES DE DONNÉES =====
        db_connections = [
            DatabaseConnectionModel(
                id=str(uuid.uuid4()),
                name="PostgreSQL Production",
                db_type=DBType.POSTGRESQL if hasattr(DBType, "POSTGRESQL") else list(DBType)[0], # fallback de sécurité
                host="12.34.56.78",
                port=5432,
                username="adawlato_prod",
                password="supersecurepassword",
                database_name="adawlato_db",
                user_id=user1.id
            ),
            DatabaseConnectionModel(
                id=str(uuid.uuid4()),
                name="MySQL Analytics",
                db_type=DBType.MYSQL if hasattr(DBType, "MYSQL") else list(DBType)[0],
                host="87.65.43.21",
                port=3306,
                username="ama_analyst",
                password="anothersecurepassword",
                database_name="ama_data",
                user_id=user2.id
            )
        ]
        db.add_all(db_connections)
        db.commit()
        print("Connexions BDD créées")

        # ===== DOCUMENTS =====
        now = datetime.now()
        documents = [
            DocumentModel(
                id=str(uuid.uuid4()),
                name="ventes_mars_2024.csv",
                type=TypeDocument.CSV,
                taille=1024,
                content="date,produit,montant\n2024-03-01,Riz,50000\n2024-03-02,Huile,30000",
                upload_date=now - timedelta(days=5),
                user_id=user1.id,
                extracted_via_ocr=False
            ),
            DocumentModel(
                id=str(uuid.uuid4()),
                name="stock_avril_2024.xlsx",
                type=TypeDocument.EXCEL,
                taille=2048,
                content="produit,quantite,prix_unitaire\nRiz,500,5000\nHuile,200,3000",
                upload_date=now - timedelta(days=2),
                user_id=user1.id,
                extracted_via_ocr=False
            ),
            DocumentModel(
                id=str(uuid.uuid4()),
                name="facture_fournisseur.png",
                type=TypeDocument.IMAGE,
                taille=512,
                content="Facture Fournisseur - Montant: 150000 FCFA - Date: 15/03/2024",
                upload_date=now - timedelta(days=1),
                user_id=user1.id,
                extracted_via_ocr=True
            ),
        ]
        db.add_all(documents)
        db.commit()
        print("Documents créés")

        # ===== ALERTES =====
        alertes = [
            AlerteModel(
                id=str(uuid.uuid4()),
                type=TypeAlerte.ANOMALIE_FINANCIERE,
                content="Transaction suspecte de 3 500 000 FCFA détectée à 2h du matin",
                send_date=now - timedelta(hours=5),
                niveau_gravite=NiveauVul.CRITIQUE,
                user_id=user1.id
            ),
            AlerteModel(
                id=str(uuid.uuid4()),
                type=TypeAlerte.PIC_DONNEES,
                content="Vos ventes ont augmenté de 12% cette semaine — continuez sur cette lancée !",
                send_date=now - timedelta(days=1),
                niveau_gravite=NiveauVul.MOYENNE,
                user_id=user1.id
            ),
            AlerteModel(
                id=str(uuid.uuid4()),
                type=TypeAlerte.ANOMALIE_VENTES,
                content="Stock de riz parfumé en rupture dans 3 jours au rythme actuel",
                send_date=now - timedelta(hours=12),
                niveau_gravite=NiveauVul.MOYENNE,
                user_id=user1.id
            ),
        ]
        db.add_all(alertes)
        db.commit()
        print("Alertes créées")

        # ===== REQUETES =====
        requete1 = RequeteModel(
            id=str(uuid.uuid4()),
            type=TypeRequete.VULGARISATION,
            content="Comment vont mes ventes ce mois ?",
            send_date=now - timedelta(hours=2),
            user_id=user1.id
        )
        requete2 = RequeteModel(
            id=str(uuid.uuid4()),
            type=TypeRequete.VULGARISATION,
            content="Prédit mes ventes pour les 30 prochains jours",
            send_date=now - timedelta(days=1),
            user_id=user1.id
        )
        db.add_all([requete1, requete2])
        db.commit()
        print("Requêtes créées")

        # ===== REPONSES =====
        reponses = [
            ReponseModel(
                id=str(uuid.uuid4()),
                type=TypeReponse.EXPLICATION,
                content="Vos ventes de mars s'élèvent à 450 000 FCFA, en hausse de 12% par rapport à février. Votre meilleur jour a été le vendredi 14 avec 45 000 FCFA.",
                received_at=now - timedelta(hours=2),
                received_by="TinyLlama",
                requete_id=requete1.id
            ),
            ReponseModel(
                id=str(uuid.uuid4()),
                type=TypeReponse.EXPLICATION,
                content="Selon vos données historiques, vos ventes devraient atteindre 185 000 FCFA la semaine prochaine. Tendance stable avec une légère hausse le vendredi.",
                received_at=now - timedelta(days=1),
                received_by="XGBoost + TinyLlama",
                requete_id=requete2.id
            ),
        ]
        db.add_all(reponses)
        db.commit()
        print("Réponses créées")

        # ===== RAPPORTS =====
        # Les rapports ci-dessous fournissent des données JSON brutes pour le parsing dans recuperer_dataframe_utilisateur
        rapports = [
            RapportModel(
                id=str(uuid.uuid4()),
                type=TypeRapport.PREPROCESSING,
                content='[{"date": "2024-03-01", "ventes": 120, "montant": 50000}, {"date": "2024-03-02", "ventes": 150, "montant": 62000}]',
                periode="Mars 2024",
                date_generation=now - timedelta(days=3),
                user_id=user1.id
            ),
            RapportModel(
                id=str(uuid.uuid4()),
                type=TypeRapport.PREPROCESSING,
                content='[{"date": "2024-04-08", "ventes": 110, "montant": 48000}, {"date": "2024-04-09", "ventes": 135, "montant": 55000}]',
                periode="Semaine 15 - 2024",
                date_generation=now - timedelta(days=1),
                user_id=user1.id
            ),
        ]
        db.add_all(rapports)
        db.commit()
        print("Rapports créés")

        # ===== VULNERABILITES =====
        vulnerabilites = [
            VulnerabiliteModel(
                id=str(uuid.uuid4()),
                type=TypeVulnerabilite.DONNEES_EXPOSEES,
                niveau=NiveauVul.CRITIQUE,
                description="Données clients stockées en clair dans un fichier Excel accessible à tous les employés",
                date_detected=now - timedelta(days=2),
                status=Status.DETECTED if hasattr(Status, "DETECTED") else Status.SUGGEREE,
                user_id=user1.id
            ),
            VulnerabiliteModel(
                id=str(uuid.uuid4()),
                type=TypeVulnerabilite.ACCES_NON_AUTORISE,
                niveau=NiveauVul.MOYENNE,
                description="3 tentatives de connexion échouées détectées sur le compte admin en 5 minutes",
                date_detected=now - timedelta(hours=6),
                status=Status.SUGGEREE,
                user_id=user1.id
            ),
        ]
        db.add_all(vulnerabilites)
        db.commit()
        print("Vulnérabilités créées")

        # ===== DECISIONS =====
        decisions = [
            DecisionModel(
                id=str(uuid.uuid4()),
                content="Augmenter le stock de riz parfumé de 200 unités",
                description="Suite à l'analyse des ventes, le riz parfumé représente 35% du CA. Une augmentation du stock s'impose avant la période de fête.",
                date=now - timedelta(days=1),
                status=Status.SUGGEREE,
                user_id=user1.id,
                reponse_id=reponses[0].id
            ),
            DecisionModel(
                id=str(uuid.uuid4()),
                content="Chiffrer les données clients",
                description="Suite à la détection d'une faille de sécurité, les données clients doivent être chiffrées immédiatement.",
                date=now - timedelta(hours=3),
                status=Status.SUGGEREE,
                user_id=user1.id,
                reponse_id=reponses[1].id
            ),
        ]
        db.add_all(decisions)
        db.commit()
        print("Décisions créées")

        print("\nSeeding terminé avec succès !")
        print(f"Users créés : koffi@example.com / password123 (cible: {user1.alerte_colonne_cible}, freq: {user1.alerte_frequence})")
        print(f"             ama@example.com / password123 (cible: {user2.alerte_colonne_cible}, freq: {user2.alerte_frequence})")
        print(f"             admin@klaaro.com / admin123")

if __name__ == "__main__":
    seed()