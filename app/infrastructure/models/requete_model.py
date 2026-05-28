from datetime import datetime

from sqlalchemy import Column, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

from app.entities.enum.typeRequete import TypeRequete
from app.infrastructure.database import Base


class RequeteModel(Base):
    __tablename__ = 'requete'

    id = Column(String, primary_key=True)
    type = Column(Enum(TypeRequete), nullable=False)
    content = Column(String, nullable=False)
    send_date = Column(DateTime, nullable=False)

    # ajout de fk
    user_id = Column(String, ForeignKey('user.id'), nullable=False)
    users = relationship("UserModel", back_populates="requetes")

    response = relationship("ResponseModel", back_populates="requetes")