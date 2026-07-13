from abc import ABC, abstractmethod
from typing import List

from app.entities.document import Document


class DocumentRepository(ABC):

    @abstractmethod
    def save_document(self, document: Document) -> Document:
        pass

    @abstractmethod
    def update_document(self, document: Document) -> Document:
        pass

    @abstractmethod
    def find_by_id(self, document_id: str) -> Document:
        pass

    @abstractmethod
    def find_all(self) -> List[Document]:
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> list[Document]:
        pass