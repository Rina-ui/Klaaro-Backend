from app.use_cases.repositories.document_repository import DocumentRepository


class FindDocumentsByUser:
    def __init__(self, repo: DocumentRepository):
        self.repo = repo

    def execute(self, user_id: str):
        return self.repo.find_by_user_id(user_id)