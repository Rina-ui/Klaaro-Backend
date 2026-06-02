from abc import ABC, abstractmethod
from typing import List
from app.entities.decision import Decision


class DecisionRepository(ABC):

    @abstractmethod
    def save_decision(self, decision: Decision) -> Decision:
        pass

    @abstractmethod
    def update_decision(self, decision: Decision) -> Decision:
        pass

    @abstractmethod
    def find_decision_by_id(self, decision_id: str) -> Decision:
        pass

    @abstractmethod
    def find_all(self) -> List[Decision]:
        pass

    @abstractmethod
    def delete_decision(self, decision_id: str) -> None:
        pass