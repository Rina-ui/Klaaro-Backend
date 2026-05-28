from sqlalchemy import Column, String, Enum
from app.infrastructure.database import Base
from app.entities.enum.role import Role

class UserModel(Base):
    __tablename__ = 'user'

    id = Column(String, primary_key=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    profession = Column(String, nullable=False)
    role = Column (Enum(Role), nullable=False)