from sqlalchemy import Column, Enum, String
from sqlalchemy.orm import DeclarativeBase

from app.entities.enum.NiveauVul import NiveauVul
from app.entities.enum.Status import Status
from app.entities.enum.typeVulnerabilite import TypeVulnerabilite


class Base(DeclarativeBase):
    pass

class VulnerabiliteModel(Base):
    __tablename__ = 'vulnerabilites'

    id = Column(String, primary_key=True)
    type = Column(Enum(TypeVulnerabilite), nullable=False)
    niveau = Column(Enum(NiveauVul), nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(Status), nullable=False)