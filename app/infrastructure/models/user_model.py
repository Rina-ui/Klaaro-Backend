from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.orm import relationship

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
    role = Column (Enum(Role), nullable=False)

    # ajout des fk
    entreprise_id = Column(String, ForeignKey('entreprise.id'), nullable=False)
    entreprise = relationship("EntrepriseModel", back_populates="users")
    alerte = relationship("AlerteModel", back_populates="users")
    decision = relationship("DecisionModel", back_populates="users")
    documents = relationship("DocumentModel", back_populates="users")
    rapport = relationship("RapportModel", back_populates="users")
    requetes = relationship("RequeteModel", back_populates="users")
    vulnerabilite = relationship("VulnerabiliteModel", back_populates="users")