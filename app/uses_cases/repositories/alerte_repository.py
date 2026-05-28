from abc import ABC, abstractmethod
from typing import List

from app.entities.alerte import Alerte


class AlerteRepository(ABC):

    @abstractmethod
    def save(self, alerte: Alerte) -> Alerte:
        pass

    @abstractmethod
    def update_alert(self, alerte: Alerte) -> Alerte:
        pass

    @abstractmethod
    def find_by_id(self, alerte_id: str) -> Alerte:
        pass

    @abstractmethod
    def find_all(self) -> List[Alerte]:
        pass

    @abstractmethod
    def delete(self, alerte_id: str) -> None:
        pass