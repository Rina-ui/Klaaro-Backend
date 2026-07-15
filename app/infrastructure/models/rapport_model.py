from sqlalchemy import Column, DateTime, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.entities.enum.typeRapport import TypeRapport
from app.infrastructure.database import Base

class RapportModel(Base):
    __tablename__ = 'rapport'

    id = Column(String, primary_key=True)
    type = Column(Enum(TypeRapport), nullable=False)
    content = Column(String, nullable=False)
    periode = Column(String, nullable=False)
    date_generation = Column(DateTime, nullable=False)

    # Clé Étrangère
    user_id = Column(String, ForeignKey('user.id'), nullable=False)

    # Relations
    user = relationship("UserModel", back_populates="rapports")
    requetes = relationship("RequeteModel", back_populates="rapport", cascade="all, delete-orphan")