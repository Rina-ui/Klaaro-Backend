from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.entities.enum.typeReponse import TypeReponse
from app.infrastructure.database import Base

class ReponseModel(Base):
    __tablename__ = 'reponse'

    id = Column(String, primary_key=True)
    type = Column(Enum(TypeReponse), nullable=False)
    content = Column(String, nullable=False)
    received_at = Column(DateTime, nullable=False)
    received_by = Column(String, nullable=False)

    # Clé Étrangère
    requete_id = Column(String, ForeignKey('requete.id'), nullable=False)

    # Relations
    requete = relationship("RequeteModel", back_populates="reponse")
    decisions = relationship("DecisionModel", back_populates="reponse", cascade="all, delete-orphan")