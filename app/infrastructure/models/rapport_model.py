from sqlalchemy import Column, DateTime, String

from app.infrastructure.database import Base


class RapportModel(Base):
    __tablename__ = 'rapport'

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    content = Column(String, nullable=False)
    periode = Column(String, nullable=False)
    date_generation = Column(DateTime, nullable=False)