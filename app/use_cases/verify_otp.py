from datetime import datetime
from app.entities.user import User
from app.use_cases.services.user.create_user import pending_registrations

class InvalidOTPException(Exception):
    pass

class VerifyOTP:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self, email: str, code: str):
        clean_email = email.lower().strip()
        record = pending_registrations.get(clean_email)

        if not record:
            raise InvalidOTPException("Aucune inscription en attente pour cet email.")

        if datetime.utcnow() > record["expires_at"]:
            del pending_registrations[clean_email]
            raise InvalidOTPException("Code OTP expiré. Veuillez recommencer l'inscription.")

        if record["code"] != code:
            record["attempts"] += 1
            if record["attempts"] >= 3:
                del pending_registrations[clean_email]
                raise InvalidOTPException("Trop de tentatives échouées. Veuillez recommencer l'inscription.")
            raise InvalidOTPException("Code OTP incorrect.")

        # Récupération des données et enregistrement effectif en BDD
        user_info = record["user_data"]
        user = User(
            id=user_info["id"],
            firstname=user_info["firstname"],
            lastname=user_info["lastname"],
            email=user_info["email"],
            password=user_info["password"],
            profession=user_info["profession"],
            role=user_info["role"],
            account_type=user_info["account_type"],
            entreprise_id=user_info["entreprise_id"]
        )

        saved_user = self.user_repository.save_user(user)

        # Nettoyage de la mémoire
        del pending_registrations[clean_email]

        return saved_user