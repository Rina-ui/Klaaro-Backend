import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# URL de connexion PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("La variable d'environnement DATABASE_URL est introuvable.")

# =========================================================================
# CRÉATION DU MOTEUR AVEC SÉCURITÉ SSL ET RECONNEXION AUTOMATIQUE (POOL)
# =========================================================================
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Teste la connexion avant chaque requête (évite SSL closed unexpectedly)
    pool_recycle=300,    # Reconnecte proprement les connexions inactives (5 minutes)
    pool_size=10,        # Nombre de connexions maintenues ouvertes
    max_overflow=20      # Connections temporaires supplémentaires sous charge
)

# Crée la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles SQLAlchemy
class Base(DeclarativeBase):
    pass

# =========================================================================
# IMPORTATION DE TOUS LES MODÈLES
# Enregistre tous les mappers SQLAlchemy au démarrage de l'application
# =========================================================================
try:
    from app.infrastructure.models.user_model import UserModel
    from app.infrastructure.models.database_model import DatabaseConnectionModel
    from app.infrastructure.models.document_model import DocumentModel
    from app.infrastructure.models.rapport_model import RapportModel
    from app.infrastructure.models.alerte_model import AlerteModel
except ImportError as e:
    print(f"⚠️ Avertissement lors du chargement des modèles SQLAlchemy : {e}")

# Dépendance FastAPI pour injecter la session de BDD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()