from datetime import datetime
from tokenize import String


from sqlalchemy import Column, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

class RapportModel(Base):
    __tablename__ = 'rapport'

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    content = Column(String, nullable=False)
    periode = Column(String, nullable=False)
    date_generation = Column(DateTime, nullable=False)