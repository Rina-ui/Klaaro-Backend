from sqlalchemy import Column, String, Integer, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase

from app.entities.enum.typeDocument import TypeDocument


class Base(DeclarativeBase):
    pass

class DocumentModel(Base):
    __tablename__ = 'document'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(Enum(TypeDocument), nullable=False)
    taille = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    upload_date = Column(DateTime, nullable=False)