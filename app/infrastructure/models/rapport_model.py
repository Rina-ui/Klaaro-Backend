from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class RapportModel(Base):
    __tablename__ = 'rapport'

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    content = Column(String, nullable=False)
    periode = Column(String, nullable=False)
    date_generation = Column(DateTime, nullable=False)

    # ajout de fk
    user_id = Column(String, ForeignKey('user.id'), nullable=False)
    users = relationship("UserModel", back_populates="rapport")