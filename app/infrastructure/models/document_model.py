from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Boolean
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
    extracted_via_ocr = Column(Boolean, default=False, nullable=False)

    # clé étrangère
    user_id = Column(String, ForeignKey('user.id'), nullable=False)