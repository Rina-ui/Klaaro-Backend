class UpdateUser:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self, user):

        return self.user_repository.update_user(user)