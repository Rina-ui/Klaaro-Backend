from sqlalchemy.orm import Session

from app.entities.document import Document
from app.infrastructure.models.document_model import DocumentModel
from app.uses_cases.repositories.document_repository import DocumentRepository


class DocumentRepositoryImpl(DocumentRepository):

    def __init__(self, db: Session) -> None:
        self.db = db

    def save_document(self, document: Document):
        model = DocumentModel(**document.__dict__)

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return document

    def update_document(self, document: Document):
        pass

    def find_by_id(self, document_id: str):
        return (
            self.db.query(DocumentModel)
            .filter(DocumentModel.id == document_id)
            .first()
        )

    def find_all(self):
        return self.db.query(DocumentModel).all()

    def delete_document(self, document_id: str):
        model = (
            self.db.query(DocumentModel)
            .filter(DocumentModel.id == document_id)
            .first()
        )

        if model:
            self.db.delete(model)
            self.db.commit()