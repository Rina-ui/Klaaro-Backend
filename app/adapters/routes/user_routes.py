import io
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd
from jose import jwt

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from pydantic import BaseModel, EmailStr, json
from sqlalchemy.orm import Session

# Dépendances et Base de données
from app.adapters.dependencies import get_current_user
from app.infrastructure.database import get_db

# Schémas
from app.adapters.schemas.user_schema import (
    UserResponse,
    UserRequest,
    LoginResponse,
    LoginRequest,
    UpdateAlertePreferencesRequest
)
from app.infrastructure.models.rapport_model import RapportModel

# Modèles et Repositories
from app.infrastructure.models.user_model import UserModel
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from app.infrastructure.repositories.alerte_repository_impl import AlerteRepositoryImpl
from app.use_cases.services.email_service import EmailService

# Cas d'utilisation (Use Cases) et Services
from app.use_cases.services.user.authenticate_user import AuthenticateUser
from app.use_cases.services.user.create_user import CreateUser
from app.use_cases.services.user.delete_user import DeleteUser
from app.use_cases.services.user.find_user_by_id import FindUserById
from app.use_cases.services.alerte.generer_alerte_prediction import GenererAlertePrediction
from app.use_cases.verify_otp import VerifyOTP

router = APIRouter(prefix="/user", tags=["User"])

SECRET_KEY = os.getenv("SECRET_KEY", "klaaro_secret_key")
ALGORITHM = "HS256"


# --- NOUVEAU SCHÉMA POUR LA VÉRIFICATION OTP ---
class VerifyOTPRequest(BaseModel):
    email: EmailStr
    code: str


# --- FONCTION HELPER ---
def recuperer_dataframe_utilisateur(user_id: int, db: Session) -> pd.DataFrame | None:
    """
    Récupère le dernier rapport de l'utilisateur en base de données
    et le convertit en DataFrame Pandas.
    """
    try:
        dernier_rapport = db.query(RapportModel).filter(
            RapportModel.user_id == user_id
        ).order_by(RapportModel.id.desc()).first()

        if not dernier_rapport or not dernier_rapport.content:
            print(f"Aucun rapport trouvé pour l'utilisateur {user_id}")
            return None

        try:
            if isinstance(dernier_rapport.content, str):
                data = json.loads(dernier_rapport.content)
            else:
                data = dernier_rapport.content

            df = pd.DataFrame(data)
            return df
        except Exception as json_err:
            print(f"La lecture JSON a échoué ({json_err}), tentative de lecture brute CSV...")
            df = pd.read_csv(io.StringIO(str(dernier_rapport.content)))
            return df

    except Exception as e:
        print(f"Erreur lors de la récupération du DataFrame pour l'utilisateur {user_id} : {e}")
        return None


# --- 1. ENREGISTREMENT ET VÉRIFICATION OTP ---

@router.post("/register")
def register(request: UserRequest, db: Session = Depends(get_db)):
    """
    Étape 1 de l'inscription : Valide les infos, génère un OTP et l'envoie par mail.
    """
    try:
        repo = UserRepositoryImpl(db)
        email_service = EmailService()
        use_case = CreateUser(repo, email_service)

        return use_case.execute(
            firstname=request.firstname,
            lastname=request.lastname,
            email=request.email,
            password=request.password,
            profession=request.profession,
            role=request.role,
            account_type=request.account_type
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-otp", response_model=LoginResponse)
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    Étape 2 de l'inscription : Valide l'OTP, enregistre l'utilisateur en BDD et génère son JWT.
    """
    try:
        repo = UserRepositoryImpl(db)
        use_case = VerifyOTP(repo)

        # Validation OTP + enregistrement BDD
        user = use_case.execute(
            email=request.email,
            code=request.code
        )

        # Génération du JWT
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user=user
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- 2. CONNEXION DIRECTE (LOGIN) ---

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Connexion standard : Vérifie les identifiants et renvoie directement le Token JWT.
    """
    try:
        repo = UserRepositoryImpl(db)
        use_case = AuthenticateUser(repo)

        user = use_case.execute(
            email=request.email,
            password=request.password
        )

        # Génération directe du Token JWT
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user=user
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-otp", response_model=LoginResponse)
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    Étape 2 de connexion : Valide le code OTP saisi et délivre le JWT final.
    """
    try:
        repo = UserRepositoryImpl(db)
        use_case = VerifyOTP(repo)

        # 1. Validation de l'OTP
        user = use_case.execute(
            email=request.email,
            code=request.code
        )

        # 2. Génération du token JWT d'accès
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user=user
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 2. PROFIL ET PRÉFÉRENCES

@router.get("/me", response_model=UserResponse)
def get_me(current_user = Depends(get_current_user)):
    """
    Récupère le profil de l'utilisateur connecté.
    """
    return current_user


@router.get("/members", response_model=List[UserResponse])
def get_collaborators(
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
):
    """
    Récupère la liste des collaborateurs appartenant à la même organisation / type de compte,
    en excluant l'utilisateur connecté.
    """
    try:
        if not current_user.account_type:
            return []

        query = db.query(UserModel).filter(
            UserModel.account_type == current_user.account_type,
            UserModel.id != current_user.id
        )

        if hasattr(UserModel, 'entreprise_id') and getattr(current_user, 'entreprise_id', None):
            query = query.filter(UserModel.entreprise_id == current_user.entreprise_id)

        users = query.all()

        result = []
        for u in users:
            user_data = UserResponse(
                id=str(u.id),
                firstname=u.firstname,
                lastname=u.lastname,
                email=u.email,
                profession=u.profession or "",
                role=u.role,
                account_type=u.account_type
            )
            result.append(user_data)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des membres : {str(e)}"
        )


@router.patch("/preferences-alertes", status_code=status.HTTP_200_OK)
def update_alerte_preferences(
        request: UpdateAlertePreferencesRequest,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    """
    Met à jour la fréquence et la colonne cible des alertes de l'utilisateur,
    et tente de générer une première alerte immédiate si des données existent.
    """
    try:
        user_model = db.query(UserModel).filter(UserModel.id == current_user.id).first()
        if not user_model:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        if request.alerte_frequence not in ["chaque_jour", "toutes_les_semaines"]:
            raise HTTPException(
                status_code=400,
                detail="La fréquence doit être 'chaque_jour' ou 'toutes_les_semaines'."
            )

        user_model.alerte_frequence = request.alerte_frequence
        user_model.alerte_colonne_cible = request.alerte_colonne_cible.strip().lower()

        db.commit()
        db.refresh(user_model)

        df_donnees = recuperer_dataframe_utilisateur(user_model.id, db)
        alerte_creee = None

        if df_donnees is not None and not df_donnees.empty:
            alerte_repo = AlerteRepositoryImpl(db)
            service_alerte = GenererAlertePrediction(alerte_repo)

            alerte_creee = service_alerte.execute(
                user_id=user_model.id,
                df_donnees=df_donnees,
                colonne_cible=user_model.alerte_colonne_cible,
                n_jours=30
            )

        return {
            "status": "success",
            "message": "Préférences d'alertes mises à jour.",
            "preferences": {
                "alerte_frequence": user_model.alerte_frequence,
                "alerte_colonne_cible": user_model.alerte_colonne_cible
            },
            "alerte_immediate_generee": alerte_creee is not None
        }

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la mise à jour des préférences : {str(e)}"
        )


# 3. ACTIONS SUR UN UTILISATEUR SPÉCIFIQUE

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
        user_id: str,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    try:
        repo = UserRepositoryImpl(db)
        use_case = FindUserById(repo)
        return use_case.execute(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
        user_id: str,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    try:
        repo = UserRepositoryImpl(db)
        use_case = DeleteUser(repo)
        use_case.execute(user_id)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))