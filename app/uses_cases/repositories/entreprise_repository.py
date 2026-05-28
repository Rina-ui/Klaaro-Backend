from abc import ABC
from typing import List

from app.entities.entreprise import Entreprise


class EntrepriseRepository(ABC):

    @staticmethod
    def save_entreprise(entreprise: Entreprise):
        pass 

    @staticmethod
    def update_entreprise(entreprise: Entreprise):
        pass

    @staticmethod
    def find_by_id(entreprise_id: str):
        pass

    @staticmethod
    def find_all(self) -> List[Entreprise]:
        pass

    @staticmethod
    def delete_entreprise(entreprise_id: str):
        pass