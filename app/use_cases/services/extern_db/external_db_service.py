from sqlalchemy import create_engine, text

from app.entities.database_connection import DatabaseConnection


class ExternalDbService:
    @staticmethod
    def test_connection(connection: DatabaseConnection) -> bool:
        """ Permet de tester si les identifiants fournis par l'utilisateur sont valides """
        try:
            url = connection.get_connection_string()
            # On crée un engine temporaire vers la base de données du client
            engine = create_engine(url, connect_args={"connect_timeout": 5})
            with engine.connect() as conn:
                conn.execute(text("SELECT 1")) # Petite requête de ping simple
            return True
        except Exception as e:
            print(f"Échec de connexion externe : {e}")
            return False

    @staticmethod
    def fetch_table_data(connection: DatabaseConnection, table_name: str, limit: int = 100):
        """ Récupère les données d'une table spécifique de l'utilisateur pour tes analyses """
        url = connection.get_connection_string()
        engine = create_engine(url)
        with engine.connect() as conn:
            # Sécurise bien l'injection du nom de la table ici si besoin
            result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
            return [dict(row) for row in result.mappings()]