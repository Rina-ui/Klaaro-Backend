from tokenize import String

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import DeclarativeBase, relationship

from app.infrastructure.database import Base


class EntrepriseModel(Base):
    __tablename__ = 'entreprise'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    number = Column(String, nullable=False)
    location = Column(String, nullable=False)
    creation_date = Column(DateTime, nullable=False)

    # ajout des relations
    users = relationship("UserModel", back_populates="entreprise")