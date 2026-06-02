from app.use_cases.repositories.document_repository import DocumentRepository

class FindDocumentsByUser:
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository

    def execute(self, user_id: str):
        return self.document_repository.find_by_id(user_id)
