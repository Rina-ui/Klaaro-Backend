from app.use_cases.repositories.user_repository import UserRepository

class FindAllUsers:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self):
        return self.user_repository.find_all()
