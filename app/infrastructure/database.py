from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

# URL de connexion PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Crée le moteur
engine = create_engine(DATABASE_URL)

# Crée la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles (déclarée en premier)
class Base(DeclarativeBase):
    pass

# =========================================================================
# FORCE L'IMPORTATION DES MODÈLES APRÈS LA DÉCLARATION DE 'Base'
# Cela permet d'enregistrer tous les mappers SQLAlchemy au démarrage de l'app
# =========================================================================
try:
    from app.infrastructure.models.user_model import UserModel
    from app.infrastructure.models.database_model import DatabaseConnectionModel
    # Ajoute les autres modèles ici au fur et à mesure :
    # from app.infrastructure.models.document_model import DocumentModel
    # from app.infrastructure.models.alerte_model import AlerteModel
    # etc...
except ImportError as e:
    # Optionnel : log l'erreur ou laisse-la remonter pour débugger tes chemins d'imports
    print(f"Erreur lors du chargement des modèles SQLAlchemy : {e}")

# Fonction pour obtenir la session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()