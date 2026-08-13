import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext

from app.entities.user import User
from app.entities.enum.account_type import AccountType
from app.use_cases.repositories.user_repository import UserRepository
from app.use_cases.services.email_service import EmailService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Stockage temporaire des inscriptions en attente d'OTP
pending_registrations = {}

class EmailAlreadyExistsException(Exception):
    pass

class CreateUser:
    def __init__(self, user_repository: UserRepository, email_service: EmailService):
        self.user_repository = user_repository
        self.email_service = email_service

    def execute(
            self,
            firstname: str,
            lastname: str,
            email: str,
            password: str,
            profession: str,
            account_type: AccountType,
            role: str = "user",
            entreprise_id: Optional[str] = None
    ) -> dict:

        clean_email = email.lower().strip()

        # 1. Vérification d'unicité de l'email
        existing_user = self.user_repository.find_by_email(clean_email)
        if existing_user:
            raise EmailAlreadyExistsException(f"L'adresse email {clean_email} est déjà associée à un compte.")

        # 2. Hachage du mot de passe
        hashed_password = pwd_context.hash(password)

        # 3. Génération du code OTP
        otp_code = f"{secrets.randbelow(1000000):06d}"
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        # 4. Stockage temporaire
        pending_registrations[clean_email] = {
            "user_data": {
                "id": str(uuid.uuid4()),
                "firstname": firstname,
                "lastname": lastname,
                "email": clean_email,
                "password": hashed_password,
                "profession": profession,
                "role": role,
                "account_type": account_type,
                "entreprise_id": entreprise_id
            },
            "code": otp_code,
            "expires_at": expires_at,
            "attempts": 0
        }

        # 5. Envoi du mail
        try:
            self.email_service.send_otp(clean_email, firstname, otp_code)
        except Exception as e:
            print(f"Erreur envoi email OTP: {e}")

        return {
            "mfa_required": True,
            "email": clean_email,
            "message": "Un code de vérification a été envoyé par email pour valider votre inscription."
        }