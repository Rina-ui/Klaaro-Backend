from passlib.context import CryptContext
from app.use_cases.repositories.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class InvalidCredentialsException(Exception):
    pass

class AuthenticateUser:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, email: str, password: str):
        clean_email = email.lower().strip()
        user = self.user_repository.find_by_email(clean_email)
        if not user:
            raise InvalidCredentialsException("Identifiants incorrects.")

        try:
            if not pwd_context.verify(password, user.password):
                raise InvalidCredentialsException("Identifiants incorrects.")
        except Exception:
            raise InvalidCredentialsException("Identifiants incorrects.")

        return user