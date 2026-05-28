from abc import ABC, abstractmethod
from typing import List

from app.entities.reponse import Reponse


class ReponseRepository(ABC):

    @abstractmethod
    def save_response(self, reponse: Reponse) -> Reponse:
        pass

    @abstractmethod
    def find_by_id(self, response_id: str) -> Reponse:
        pass

    @abstractmethod
    def find_all(self) -> List[Reponse]:
        pass

    @abstractmethod
    def delete_response(self, reponse_id: str) -> None:
        pass