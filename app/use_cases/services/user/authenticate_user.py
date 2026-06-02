from passlib.context import CryptContext
from app.use_cases.repositories.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthenticateUser:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, email: str, password: str):
        user = self.user_repository.find_by_email(email)
        if not user:
            raise Exception("Utilisateur non trouve")
        if not pwd_context.verify(password, user.password):
            raise Exception("Mot de passe incorrect")
        return user
