from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from app.infrastructure.database import Base
from app.entities.enum.dbType import DBType

class DatabaseConnectionModel(Base):
    __tablename__ = 'user_database_connections'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    db_type = Column(Enum(DBType), nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    database_name = Column(String, nullable=False)

    user_id = Column(String, ForeignKey('user.id'), nullable=False)