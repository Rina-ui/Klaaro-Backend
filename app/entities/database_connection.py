from uuid import uuid4
from app.entities.enum.dbType import DBType

class DatabaseConnection:
    def __init__(self, name: str, db_type: DBType, host: str, port: int, username: str, password: str, database_name: str, user_id: str, id: str = None):
        self.id = id or str(uuid4())
        self.name = name         
        self.db_type = db_type
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database_name = database_name
        self.user_id = user_id

    # méthode dynamique qui génère l'URL SQLAlchemy pour se connecter à la base
    def get_connection_string(self) -> str:
        if self.db_type == DBType.POSTGRESQL:
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}"
        elif self.db_type == DBType.MYSQL:
            return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}"
        raise ValueError("Type de base de données non supporté")