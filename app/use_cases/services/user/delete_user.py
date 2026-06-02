from app.use_cases.repositories.user_repository import UserRepository

class DeleteUser:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: str) -> None:
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise Exception("Utilisateur non trouve")
        self.user_repository.delete_user(user_id)
