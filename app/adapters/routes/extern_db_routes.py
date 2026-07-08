from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.entities.database_connection import DatabaseConnection
from app.entities.enum.dbType import DBType
from app.infrastructure.database import get_db
from app.use_cases.services.extern_db.external_db_service import ExternalDbService

router = APIRouter(prefix="/databases", tags=["Databases"])

@router.post("/connect")
def connect_user_database(payload: dict, user_id: str, db: Session = Depends(get_db)):
    # instancier l'entité avec ce que l'utilisateur a tapé sur le formulaire Front
    conn_entity = DatabaseConnection(
        name=payload["name"],
        db_type=DBType(payload["db_type"]),
        host=payload["host"],
        port=payload["port"],
        username=payload["username"],
        password=payload["password"],
        database_name=payload["database_name"],
        user_id=user_id
    )

    # tester immédiatement si les identifiants marchent
    is_working = ExternalDbService.test_connection(conn_entity)
    if not is_working:
        raise HTTPException(status_code=400, detail="Impossible de se connecter à votre base de données. Vérifiez vos accès.")

    #  sauvegarde de la configuration dans notre dépôt (si c'est good)
    # repo.save(conn_entity) ...

    return {"status": "success", "message": "Base de données connectée avec succès !"}