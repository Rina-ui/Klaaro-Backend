from abc import ABC
from typing import List

from app.entities.rapport import Rapport


class RapportRepository(ABC):

    @staticmethod
    def save_rapport(rapport: Rapport):
        pass

    @staticmethod
    def update_rapport(rapport: Rapport):
        pass

    @staticmethod
    def find_by_id(rapport_id: str):
        pass

    @staticmethod
    def find_all(self) -> List[Rapport]:
        pass

    @staticmethod
    def delete_rapport(rapport_id: str):
        pass