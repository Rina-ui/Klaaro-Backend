from sqlalchemy.orm import Session

from app.entities.user import User
from app.infrastructure.models.user_model import UserModel
from app.use_cases.repositories.user_repository import UserRepository


class UserRepositoryImpl(UserRepository):

    def __init__(self, db: Session):
        self.db = db

    def save_user(self, user: User):
        model = UserModel(**user.__dict__)

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return user

    def find_all(self):
        return self.db.query(UserModel).all()

    def find_by_email(self, email: str):
        return (
            self.db.query(UserModel).
            filter(UserModel.email == email).
            first()
        )

    def find_by_firstname(self, firstname: str):
        return (
            self.db.query(UserModel)
            .filter(UserModel.firstname == firstname)
            .first()
        )

    def update_user(self, user: User):
        pass

    def find_by_id(self, user_id: str):
        return (
            self.db.query(UserModel)
            .filter(UserModel.id == user_id)
            .first()
        )

    def delete_user(self, user_id: str):
        model = (
            self.db.query(UserModel)
            .filter(UserModel.id == user_id)
            .first()
        )

        if model:
            self.db.delete(model)
            self.db.commit()
