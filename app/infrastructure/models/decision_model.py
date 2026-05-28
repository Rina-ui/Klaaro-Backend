from datetime import datetime

from sqlalchemy import Column, Enum, String, DateTime
from sqlalchemy.orm import DeclarativeBase

from app.entities.enum.Status import Status
from app.infrastructure.database import Base


class DecisionModel(Base):

    __tablename__ = 'decision'

    id = Column(String, primary_key=True)
    content = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(Status), nullable=False)
    date = Column(DateTime, nullable=False)