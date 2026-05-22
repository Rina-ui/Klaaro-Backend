from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.orm import DeclarativeBase

from app.entities.enum.NiveauVul import NiveauVul
from app.entities.enum.typeAlerte import TypeAlerte


class Base(DeclarativeBase):
    pass

class AlerteModel(Base):
    __tablename__ = 'alerte'

    id = Column(String, primary_key=True)
    type = Column(Enum(TypeAlerte), nullable=False)
    content = Column(String, nullable=False)
    send_date = Column(DateTime, nullable=False)
    niveau_gravity = Column(Enum(NiveauVul), nullable=False)