from abc import ABC
from typing import List

from app.entities.document import Document


class DocumentRepository(ABC):

    @staticmethod
    def save_document(document: Document):
        pass

    @staticmethod
    def update_document(document: Document):
        pass

    @staticmethod
    def find_by_id(document_id: str):
        pass

    @staticmethod
    def find_all(self) -> List[Document]:
        pass

    @staticmethod
    def delete_document(document_id: str):
        pass