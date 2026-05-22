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

# Base pour les modèles
class Base(DeclarativeBase):
    pass

# Fonction pour obtenir la session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()