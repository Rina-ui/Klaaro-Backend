from abc import ABC, abstractmethod

from app.entities.user import User


class UserRepository(ABC):

    @abstractmethod
    def save_user(self, user: User) -> User:
        pass

    @abstractmethod
    def find_all(self) -> list[User]:
        pass

    @abstractmethod
    def find_by_email(self, email: str):
        pass

    @abstractmethod
    def find_by_firstname(self, username: str) -> User:
        pass

    @abstractmethod
    def update_user(self, user: User) -> User:
        pass

    @abstractmethod
    def find_by_id(self, user_id: str) -> User:
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> None:
        pass
