from sqlalchemy import Column, Enum, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

from app.entities.enum.NiveauVul import NiveauVul
from app.entities.enum.Status import Status
from app.entities.enum.typeVulnerabilite import TypeVulnerabilite
from app.infrastructure.database import Base


class VulnerabiliteModel(Base):
    __tablename__ = 'vulnerabilites'

    id = Column(String, primary_key=True)
    type = Column(Enum(TypeVulnerabilite), nullable=False)
    niveau = Column(Enum(NiveauVul), nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(Status), nullable=False)
    date_detected = Column(DateTime, nullable=False)

    # ajout de fk
    user_id = Column(String, ForeignKey('user.id'), nullable=False)
    users = relationship("UserModel", back_populates="vulnerabilites")