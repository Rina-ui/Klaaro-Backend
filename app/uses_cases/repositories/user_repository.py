from abc import ABC

from app.entities.user import User


class UserRepository(ABC):

    @staticmethod
    def save_user(user: User):
        pass

    @staticmethod
    def find_all(self) -> list[User]:
        pass

    @staticmethod
    def find_by_email(email: str):
        pass

    @staticmethod
    def find_by_firstname(username: str):
        pass

    @staticmethod
    def update_user(user: User):
        pass

    @staticmethod
    def find_by_id(user_id: str):
        pass

    @staticmethod
    def delete_user(user_id: str):
        pass
