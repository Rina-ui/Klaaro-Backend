from sqlalchemy import Column, Enum, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.entities.enum.typeRequete import TypeRequete
from app.infrastructure.database import Base

class RequeteModel(Base):
    __tablename__ = 'requete'

    id = Column(String, primary_key=True)
    type = Column(Enum(TypeRequete), nullable=False)
    content = Column(String, nullable=False)
    send_date = Column(DateTime, nullable=False)

    # Clés Étrangères
    user_id = Column(String, ForeignKey('user.id'), nullable=False)
    rapport_id = Column(String, ForeignKey('rapport.id'), nullable=True)

    # Relations
    user = relationship("UserModel", back_populates="requetes")
    rapport = relationship("RapportModel", back_populates="requetes")

    # Relation un-à-un
    reponse = relationship("ReponseModel", back_populates="requete", uselist=False, cascade="all, delete-orphan")