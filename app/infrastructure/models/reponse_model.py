from datetime import datetime

from sqlalchemy import String, Column, DateTime
from sqlalchemy.orm import DeclarativeBase

from app.infrastructure.database import Base


class ReponseModel(Base):
    __tablename__ = 'reponse'

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    content = Column(String, nullable=False)
    received_at = Column(DateTime, nullable=False)
    received_by= Column(String, nullable=False)