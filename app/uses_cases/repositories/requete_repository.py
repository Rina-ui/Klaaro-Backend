from abc import ABC, abstractmethod
from typing import List

from app.entities.requete import Requete


class RequeteRepository(ABC):

    @abstractmethod
    def save_requete(self, requete: Requete) -> Requete:
        pass

    @abstractmethod
    def find_by_id(self, requete_id: str) -> Requete:
        pass

    @abstractmethod
    def find_all(self) -> List[Requete]:
        pass

    @abstractmethod
    def delete_request(self, requete_id: str) -> None:
        pass
