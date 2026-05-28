from abc import ABC
from typing import List

from app.entities.requete import Requete


class RequeteRepository(ABC):

    @staticmethod
    def save_requete(requete: Requete):
        pass

    @staticmethod
    def find_by_id(requete_id: str):
        pass

    @staticmethod
    def find_all(self) -> List[Requete]:
        pass

    @staticmethod
    def delete_request(requete_id: str):
        pass
