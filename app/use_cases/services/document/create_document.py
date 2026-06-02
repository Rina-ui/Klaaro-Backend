import uuid
from datetime import datetime
from app.entities.document import Document
from app.use_cases.repositories.document_repository import DocumentRepository

class CreateDocument:
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository

    def execute(self, name: str, type: str, taille: int, content: str, user_id: str) -> Document:
        document = Document(
            id=str(uuid.uuid4()),
            name=name,
            type=type,
            taille=taille,
            content=content,
            upload_date=datetime.utcnow(),
            user_id=user_id
        )
        return self.document_repository.save_document(document)
