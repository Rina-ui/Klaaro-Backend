from abc import ABC
from typing import List

from app.entities.alerte import Alerte


class AlerteRepository(ABC):

    @staticmethod
    def save(alerte: Alerte):
        pass

    @staticmethod
    def update_alert(alerte: Alerte):
        pass

    @staticmethod
    def find_by_id(alerte_id: str):
        pass

    @staticmethod
    def find_all(self) -> List[Alerte]:
        pass

    @staticmethod
    def delete(alerte_id: str):
        pass