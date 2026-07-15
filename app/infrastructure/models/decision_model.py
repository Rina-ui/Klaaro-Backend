from sqlalchemy import Column, Enum, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.entities.enum.Status import Status
from app.infrastructure.database import Base

class DecisionModel(Base):
    __tablename__ = 'decision'

    id = Column(String, primary_key=True)
    content = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(Status), nullable=False)
    date = Column(DateTime, nullable=False)

    # Clés Étrangères
    user_id = Column(String, ForeignKey('user.id'), nullable=False)
    reponse_id = Column(String, ForeignKey('reponse.id'), nullable=False)

    # Relations
    user = relationship("UserModel", back_populates="decisions")
    reponse = relationship("ReponseModel", back_populates="decisions")