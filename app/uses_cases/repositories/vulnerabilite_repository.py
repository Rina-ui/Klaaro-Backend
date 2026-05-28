from abc import ABC
from typing import List

from app.entities.vulnerabilite import Vulnerabilite


class VulnerabiliteRepository(ABC):

    @staticmethod
    def save_vulnerabilite(vulnerabilite: Vulnerabilite):
        pass

    @staticmethod
    def find_vulnerabilite_by_id(vulnerabilite_id: str):
        pass

    @staticmethod
    def find_all(self) -> List[Vulnerabilite]:
        pass

    @staticmethod
    def delete_vulnerabilite_by_id(vulnerabilite_id: str):
        pass 