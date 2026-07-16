from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.adapters.dependencies import get_current_user
from app.infrastructure.models.user_model import UserModel
from app.adapters.schemas.user_schema import UpdateAlertePreferencesRequest

router = APIRouter(
    prefix="/user",
    tags=["User"],
)

@router.patch("/preferences-alertes", status_code=status.HTTP_200_OK)
def update_alerte_preferences(
        request: UpdateAlertePreferencesRequest,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    try:
        # 1. Récupérer l'utilisateur en base de données
        user_model = db.query(UserModel).filter(UserModel.id == current_user.id).first()
        if not user_model:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        # 2. Valider sommairement la fréquence
        if request.alerte_frequence not in ["chaque_jour", "toutes_les_semaines"]:
            raise HTTPException(
                status_code=400,
                detail="La fréquence doit être 'chaque_jour' ou 'toutes_les_semaines'."
            )

        # 3. Mettre à jour les colonnes sur le modèle SQLAlchemy
        user_model.alerte_frequence = request.alerte_frequence
        user_model.alerte_colonne_cible = request.alerte_colonne_cible.strip().lower()

        # 4. Commit les modifications
        db.commit()
        db.refresh(user_model)

        return {
            "status": "success",
            "message": "Préférences d'alertes mises à jour avec succès",
            "preferences": {
                "alerte_frequence": user_model.alerte_frequence,
                "alerte_colonne_cible": user_model.alerte_colonne_cible
            }
        }

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la mise à jour des préférences : {str(e)}"
        )