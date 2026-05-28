from abc import ABC, abstractmethod
from typing import List

from app.entities.rapport import Rapport


class RapportRepository(ABC):

    @abstractmethod
    def save_rapport(self, rapport: Rapport) -> Rapport:
        pass

    @abstractmethod
    def update_rapport(self, rapport: Rapport) -> Rapport:
        pass

    @abstractmethod
    def find_by_id(self, rapport_id: str):
        pass

    @abstractmethod
    def find_all(self) -> List[Rapport]:
        pass

    @abstractmethod
    def delete_rapport(self, rapport_id: str) -> None:
        pass