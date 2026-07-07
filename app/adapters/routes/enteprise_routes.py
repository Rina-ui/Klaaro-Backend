from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.adapters.dependencies import get_current_user
from app.adapters.schemas.entreprise_schema import EntrepriseResponse, EntrepriseRequest
from app.infrastructure.database import get_db
from app.infrastructure.repositories.entreprise_repository_impl import EntrepriseRepositoryImpl
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl # 👈 Importe ton repo User
from app.use_cases.services.entreprise.create_entreprise import CreateEntreprise
from app.use_cases.services.entreprise.find_entreprise_by_id import FindEntrepriseById
from app.use_cases.services.entreprise.delete_entreprise import DeleteEntreprise

router = APIRouter(prefix="/enterprise", tags=["Enterprises"])

@router.post("/", response_model=EntrepriseResponse, status_code=status.HTTP_201_CREATED)
def create_entreprise(request: EntrepriseRequest, db: Session = Depends(get_db),
                      current_user = Depends(get_current_user)):
    try:
        # On instancie les deux repositories nécessaires
        repo_entreprise = EntrepriseRepositoryImpl(db)
        repo_user = UserRepositoryImpl(db)

        # On passe les deux repos au UseCase (pense à mettre à jour le __init__ de ton CreateEntreprise comme vu juste avant !)
        use_case = CreateEntreprise(repo_entreprise, repo_user)

        # On exécute en ajoutant l'ID de l'utilisateur connecté
        return use_case.execute(
            name=request.name,
            email=request.email,
            number=request.number,
            location=request.location,
            user_id=current_user.id
        )
    except Exception as e:
        # Met un status_code 400 ou 500, mais detail=str(e) te renverra la vraie erreur dans le front !
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{entreprise_id}", response_model=EntrepriseResponse)
def get_entreprise(entreprise_id: str, db: Session = Depends(get_db),
                   current_user = Depends(get_current_user)):
    try:
        repo = EntrepriseRepositoryImpl(db)
        use_case = FindEntrepriseById(repo)
        return use_case.execute(entreprise_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{entreprise_id}")
def delete_entreprise(entreprise_id: str, db: Session = Depends(get_db),
                      current_user = Depends(get_current_user)):
    try:
        repo = EntrepriseRepositoryImpl(db)
        use_case = DeleteEntreprise(repo)
        use_case.execute(entreprise_id)
        return {"message": "Enterprise deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))