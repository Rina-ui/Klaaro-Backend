from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.entities.database_connection import DatabaseConnection
from app.entities.enum.dbType import DBType
from app.infrastructure.database import get_db
from app.use_cases.services.extern_db.external_db_service import ExternalDbService
from app.adapters.dependencies import get_current_user

router = APIRouter(prefix="/databases", tags=["Databases"])

class DatabaseConnectionPayload(BaseModel):
    name: str
    db_type: DBType = Field(alias="dbType")
    host: str
    port: int
    username: str
    password: str
    database_name: str = Field(alias="databaseName")

    class Config:
        populate_by_name = True


@router.post("/connect")
def connect_user_database(
        payload: DatabaseConnectionPayload,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user),
):
    conn_entity = DatabaseConnection(
        name=payload.name,
        db_type=payload.db_type,
        host=payload.host,
        port=payload.port,
        username=payload.username,
        password=payload.password,
        database_name=payload.database_name,
        user_id=current_user.id,
    )

    is_working = ExternalDbService.test_connection(conn_entity)
    if not is_working:
        raise HTTPException(
            status_code=400,
            detail="Impossible de se connecter à votre base de données. Vérifiez vos accès."
        )

    db.add(conn_entity)
    db.commit()
    db.refresh(conn_entity)

    return {"status": "success", "message": "Base de données connectée avec succès !", "id": conn_entity.id}