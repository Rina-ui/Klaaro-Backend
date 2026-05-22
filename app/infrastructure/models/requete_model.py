from datetime import datetime

from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.orm import DeclarativeBase

from app.entities.enum.typeRequete import TypeRequete


class Base(DeclarativeBase):
    pass

class RequeteModel(Base):
    __tablename__ = 'requete'

    id = Column(String, primary_key=True)
    type = Column(Enum(TypeRequete), nullable=False)
    content = Column(String, nullable=False)
    send_date = Column(DateTime, nullable=False)