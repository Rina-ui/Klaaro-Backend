from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.adapters.dependencies import get_current_user
from app.adapters.schemas.entreprise_schema import EntrepriseResponse, EntrepriseRequest
from app.entities.user import User
from app.infrastructure.database import get_db
from app.infrastructure.repositories.entreprise_repository_impl import EntrepriseRepositoryImpl
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from app.use_cases.services.entreprise.create_entreprise import CreateEntreprise
from app.use_cases.services.entreprise.find_entreprise_by_id import FindEntrepriseById
from app.use_cases.services.entreprise.delete_entreprise import DeleteEntreprise

import uuid
from pydantic import BaseModel, EmailStr

# On crée un schéma plus complet puisqu'on crée un vrai utilisateur
class AddUserRequest(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    profession: str

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



@router.post("/add-user", status_code=status.HTTP_201_CREATED)
def add_user_to_enterprise(request: AddUserRequest, db: Session = Depends(get_db),
                           current_user = Depends(get_current_user)):
    try:
        # Vérifier que l'utilisateur connecté gère bien une entreprise
        if not current_user.entreprise_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seul l'administrateur d'une entreprise peut ajouter des collaborateurs."
            )

        repo_user = UserRepositoryImpl(db)

        # 2. Vérifier si l'email n'est pas déjà pris sur la plateforme
        existing_user = repo_user.find_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Un utilisateur avec cet email existe déjà.")

        # 3. Préparer l'entité du nouvel utilisateur
        # On génère un ID unique et un mot de passe temporaire (ex: Welcome123!)
        # Que tu pourras hasher avec ton outil de hashage (ex: pwd_context.hash("Welcome123!"))
        temp_password = "Password123!"

        new_collaborator = User(
            id=str(uuid.uuid4()),
            firstname=request.firstname,
            lastname=request.lastname,
            email=request.email,
            password=temp_password,
            profession=request.profession,
            role="member",
            account_type=current_user.account_type,
            entreprise_id=current_user.entreprise_id
        )

        # Sauvegarde via save_user puisqu'il est tout neuf !
        saved_user = repo_user.save_user(new_collaborator)

        return {
            "message": f"Le collaborateur {saved_user.firstname} a été créé avec succès.",
            "temporary_password": temp_password # Tu pourras lui afficher ou lui envoyer par mail
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))