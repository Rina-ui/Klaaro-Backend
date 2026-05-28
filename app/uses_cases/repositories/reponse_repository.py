from abc import ABC
from typing import List

from app.entities.reponse import Reponse


class ReponseRepository(ABC):

    @staticmethod
    def save_response(reponse: Reponse):
        pass

    @staticmethod
    def find_by_id(rapport_id: str):
        pass

    @staticmethod
    def find_all(self) -> List[Reponse]:
        pass

    @staticmethod
    def delete_response(rapport_id: str):
        pass