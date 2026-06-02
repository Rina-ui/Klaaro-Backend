from app.use_cases.repositories.document_repository import DocumentRepository

class DeleteDocument:
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository

    def execute(self, document_id: str) -> None:
        document = self.document_repository.find_by_id(document_id)
        if not document:
            raise Exception("Document non trouve")
        self.document_repository.delete_document(document_id)
