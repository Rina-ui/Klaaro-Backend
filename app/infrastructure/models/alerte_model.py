from sqlalchemy import Column, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

from app.entities.enum.NiveauVul import NiveauVul
from app.entities.enum.typeAlerte import TypeAlerte
from app.infrastructure.database import Base


class AlerteModel(Base):
    __tablename__ = 'alerte'

    id = Column(String, primary_key=True)
    type = Column(Enum(TypeAlerte), nullable=False)
    content = Column(String, nullable=False)
    send_date = Column(DateTime, nullable=False)
    niveau_gravity = Column(Enum(NiveauVul), nullable=False)

    # ajout de fk
    user_id = Column(String, ForeignKey('user.id'), nullable=False)
    users = relationship("UserModel", back_populates="alertes")