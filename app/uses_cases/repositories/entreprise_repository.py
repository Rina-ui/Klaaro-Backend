from abc import ABC, abstractmethod
from typing import List

from app.entities.entreprise import Entreprise


class EntrepriseRepository(ABC):

    @abstractmethod
    def save_entreprise(self, entreprise: Entreprise) -> Entreprise:
        pass

    @abstractmethod
    def update_entreprise(self, entreprise: Entreprise) -> Entreprise:
        pass

    @abstractmethod
    def find_by_id(self, entreprise_id: str) -> Entreprise:
        pass

    @abstractmethod
    def find_all(self) -> List[Entreprise]:
        pass

    @abstractmethod
    def delete_entreprise(self, entreprise_id: str) -> None:
        pass