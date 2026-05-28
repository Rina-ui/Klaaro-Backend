from abc import ABC, abstractmethod
from typing import List

from app.entities.vulnerabilite import Vulnerabilite


class VulnerabiliteRepository(ABC):

    @abstractmethod
    def save_vulnerabilite(self, vulnerabilite: Vulnerabilite) -> Vulnerabilite:
        pass

    @abstractmethod
    def find_vulnerabilite_by_id(self, vulnerabilite_id: str) -> Vulnerabilite:
        pass

    @abstractmethod
    def find_all(self) -> List[Vulnerabilite] :
        pass

    @abstractmethod
    def delete_vulnerabilite_by_id(self, vulnerabilite_id: str) -> None:
        pass 