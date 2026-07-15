from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.entities.enum.account_type import AccountType
from app.infrastructure.database import Base
from app.entities.enum.role import Role

class UserModel(Base):
    __tablename__ = 'user'

    id = Column(String, primary_key=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    profession = Column(String, nullable=False)
    role = Column(String, nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    entreprise_id = Column(String, ForeignKey('entreprise.id'), nullable=True)

    # Relation parente
    entreprise = relationship("EntrepriseModel", back_populates="users")

    # === RELATIONS ENFANTS AJOUTÉES ===
    # Ces lignes permettent de lier UserModel aux autres tables et d'éviter les erreurs de Mapper/back_populates
    documents = relationship("DocumentModel", back_populates="user", cascade="all, delete-orphan")
    alertes = relationship("AlerteModel", back_populates="user", cascade="all, delete-orphan")
    requetes = relationship("RequeteModel", back_populates="user", cascade="all, delete-orphan")
    rapports = relationship("RapportModel", back_populates="user", cascade="all, delete-orphan")
    vulnerabilites = relationship("VulnerabiliteModel", back_populates="user", cascade="all, delete-orphan")
    decisions = relationship("DecisionModel", back_populates="user", cascade="all, delete-orphan")
    database_connections = relationship("DatabaseConnectionModel", back_populates="user", cascade="all, delete-orphan")