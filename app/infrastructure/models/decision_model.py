from datetime import datetime

from sqlalchemy import Column, Enum, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

from app.entities.enum.Status import Status
from app.infrastructure.database import Base


class DecisionModel(Base):

    __tablename__ = 'decision'

    id = Column(String, primary_key=True)
    content = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(Status), nullable=False)
    date = Column(DateTime, nullable=False)

    # ajout de fk
    user_id = Column(String, ForeignKey('user.id'), nullable=False)
    users = relationship("UserModel", back_populates="decision")