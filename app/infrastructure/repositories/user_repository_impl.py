from typing import List, Any

from sqlalchemy.orm import Session

from app.entities.user import User
from app.infrastructure.models.user_model import UserModel
from app.use_cases.repositories.user_repository import UserRepository


class UserRepositoryImpl(UserRepository):

    def __init__(self, db: Session):
        self.db = db

    # Fonction utilitaire pour transformer un UserModel (BDD) en User (Entité)
    def _to_entity(self, model: UserModel) -> User:
        if not model:
            return None
        return User(
            id=model.id,
            firstname=model.firstname,
            lastname=model.lastname,
            email=model.email,
            password=model.password,
            profession=model.profession,
            role=model.role,
            account_type=model.account_type,
            entreprise_id=model.entreprise_id
        )

    def save_user(self, user: User) -> User:
        # On extrait proprement les dictionnaires sans chichis
        model = UserModel(
            id=user.id,
            firstname=user.firstname,
            lastname=user.lastname,
            email=user.email,
            password=user.password,
            profession=user.profession,
            role=user.role,
            account_type=user.account_type,
            entreprise_id=user.entreprise_id
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return self._to_entity(model)

    def find_all(self):
        models = self.db.query(UserModel).all()
        return [self._to_entity(m) for m in models]

    def find_by_email(self, email: str) -> User:
        model = (
            self.db.query(UserModel).
            filter(UserModel.email == email).
            first()
        )
        return self._to_entity(model)

    def find_by_id(self, user_id: str) -> User:
        model = (
            self.db.query(UserModel)
            .filter(UserModel.id == user_id)
            .first()
        )
        return self._to_entity(model)

    def find_by_firstname(self, firstname: str) -> User:
        model = (
            self.db.query(UserModel)
            .filter(UserModel.firstname == firstname)
            .first()
        )
        return self._to_entity(model)

    def update_user(self, user: User) -> User:
        # 1. On récupère le modèle SQL existant dans la session
        model = (
            self.db.query(UserModel)
            .filter(UserModel.id == user.id)
            .first()
        )

        if not model:
            raise Exception("Utilisateur introuvable pour la mise à jour.")

        # mettre à jour le champ de l'entreprise
        model.entreprise_id = user.entreprise_id
        # Si tu as d'autres champs modifiables, tu peux les réassigner ici

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def delete_user(self, user_id: str):
        model = (
            self.db.query(UserModel)
            .filter(UserModel.id == user_id)
            .first()
        )

        if model:
            self.db.delete(model)
            self.db.commit()

    def get_user_by_id(self, user_id: str) -> User:
        return self.find_by_id(user_id)

    def get_by_entreprise(self, entreprise_id: str | int) -> list[Any] | list[type[UserModel]]:
        """
        Récupère la liste de tous les utilisateurs appartenant à la même entreprise.
        """
        if not entreprise_id:
            return []

        return self.db.query(UserModel).filter(
            UserModel.entreprise_id == entreprise_id
        ).all()