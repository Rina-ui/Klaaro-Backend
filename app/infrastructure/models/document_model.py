from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

from app.entities.enum.typeDocument import TypeDocument
from app.infrastructure.database import Base


class DocumentModel(Base):
    __tablename__ = 'document'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(Enum(TypeDocument), nullable=False)
    taille = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    upload_date = Column(DateTime, nullable=False)

    # ajout de fk
    user_id = Column(String, ForeignKey('user.id'), nullable=False)
