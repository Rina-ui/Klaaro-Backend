import uuid
from passlib.context import CryptContext
from app.entities.user import User
from app.entities.enum.account_type import AccountType
from app.use_cases.repositories.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CreateUser:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, firstname: str, lastname: str, email: str,
                password: str, profession: str, role: str,
                account_type: AccountType, entreprise_id: str = None) -> User:
        hashed_password = pwd_context.hash(password)
        user = User(
            id=str(uuid.uuid4()),
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=hashed_password,
            profession=profession,
            role=role,
            account_type=account_type,
            entreprise_id=entreprise_id
        )
        return self.user_repository.save_user(user)
